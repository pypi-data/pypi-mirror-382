/*
 * Copyright © 2008-2011 Kristian Høgsberg
 * Copyright © 2011 Intel Corporation
 * Copyright © 2017, 2018 Collabora, Ltd.
 * Copyright © 2017, 2018 General Electric Company
 * Copyright (c) 2018 DisplayLink (UK) Ltd.
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice (including the
 * next paragraph) shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include "config.h"

#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <dlfcn.h>

#include "drm-internal.h"
#include "pixman-renderer.h"
#include "pixel-formats.h"
#include "renderer-gl/gl-renderer.h"
#include "renderer-vulkan/vulkan-renderer.h"
#include "shared/weston-assert.h"
#include "shared/weston-egl-ext.h"
#include "linux-dmabuf.h"
#include "linux-explicit-synchronization.h"

/* When initializing EGL, if the preferred buffer format isn't available
 * we may be able to substitute an ARGB format for an XRGB one.
 *
 * This returns NULL if substitution isn't possible. The caller is responsible
 * for checking for NULL before calling gl_renderer->create().
 *
 * This works around https://bugs.freedesktop.org/show_bug.cgi?id=89689
 * but it's entirely possible we'll see this again on other implementations.
 */
static const struct pixel_format_info *
fallback_format_for(const struct pixel_format_info *format)
{
	return pixel_format_get_info_by_opaque_substitute(format->format);
}

static int
drm_backend_create_gl_renderer(struct drm_backend *b)
{
	const struct pixel_format_info *format[3] = {
		b->format,
		fallback_format_for(b->format),
	};
	struct gl_renderer_display_options options = {
		.egl_platform = EGL_PLATFORM_GBM_KHR,
		.egl_native_display = b->gbm,
		.egl_surface_type = EGL_WINDOW_BIT,
		.formats = format,
		.formats_count = 1,
	};

	if (format[1])
		options.formats_count = 2;

	return weston_compositor_init_renderer(b->compositor,
					       WESTON_RENDERER_GL,
					       &options.base);
}

static int
drm_backend_create_vulkan_renderer(struct drm_backend *b)
{
	const struct pixel_format_info *format[3] = {
		b->format,
		fallback_format_for(b->format),
	};
	struct vulkan_renderer_display_options options = {
		.gbm_device = b->gbm,
		.formats = format,
		.formats_count = 1,
	};

	if (format[1])
		options.formats_count = 2;

	return weston_compositor_init_renderer(b->compositor,
					       WESTON_RENDERER_VULKAN,
					       &options.base);
}

int
init_egl(struct drm_backend *b)
{
	struct drm_device *device = b->drm;

	b->gbm = gbm_create_device(device->drm.fd);
	if (!b->gbm)
		return -1;

	if (drm_backend_create_gl_renderer(b) < 0) {
		gbm_device_destroy(b->gbm);
		b->gbm = NULL;
		return -1;
	}

	return 0;
}

int
init_vulkan(struct drm_backend *b)
{
	struct drm_device *device = b->drm;

	b->gbm = gbm_create_device(device->drm.fd);
	if (!b->gbm)
		return -1;

	if (drm_backend_create_vulkan_renderer(b) < 0) {
		gbm_device_destroy(b->gbm);
		b->gbm = NULL;
		return -1;
	}

	return 0;
}

static void drm_output_fini_cursor_egl(struct drm_output *output)
{
	unsigned int i;

	for (i = 0; i < ARRAY_LENGTH(output->gbm_cursor_fb); i++) {
		/* This cursor does not have a GBM device */
		if (output->gbm_cursor_fb[i] && !output->gbm_cursor_fb[i]->bo)
			output->gbm_cursor_fb[i]->type = BUFFER_PIXMAN_DUMB;
		drm_fb_unref(output->gbm_cursor_fb[i]);
		output->gbm_cursor_fb[i] = NULL;
	}
}

static void drm_output_fini_cursor_vulkan(struct drm_output *output)
{
	unsigned int i;

	for (i = 0; i < ARRAY_LENGTH(output->gbm_cursor_fb); i++) {
		/* This cursor does not have a GBM device */
		if (output->gbm_cursor_fb[i] && !output->gbm_cursor_fb[i]->bo)
			output->gbm_cursor_fb[i]->type = BUFFER_PIXMAN_DUMB;
		drm_fb_unref(output->gbm_cursor_fb[i]);
		output->gbm_cursor_fb[i] = NULL;
	}
}

static int
drm_output_init_cursor_egl(struct drm_output *output, struct drm_backend *b)
{
	struct drm_device *device = output->device;
	unsigned int i;

	/* No point creating cursors if we don't have a plane for them. */
	if (!output->cursor_plane)
		return 0;

	for (i = 0; i < ARRAY_LENGTH(output->gbm_cursor_fb); i++) {
		struct gbm_bo *bo;

		if (gbm_device_get_fd(b->gbm) != output->device->drm.fd) {
			output->gbm_cursor_fb[i] =
				drm_fb_create_dumb(output->device,
						   device->cursor_width,
						   device->cursor_height,
						   DRM_FORMAT_ARGB8888);
			/* Override buffer type, since we know it is a cursor */
			output->gbm_cursor_fb[i]->type = BUFFER_CURSOR;
			output->gbm_cursor_handle[i] =
				output->gbm_cursor_fb[i]->handles[0];
		} else {
			bo = gbm_bo_create(b->gbm, device->cursor_width, device->cursor_height,
					   GBM_FORMAT_ARGB8888,
					   GBM_BO_USE_CURSOR | GBM_BO_USE_WRITE);
			if (!bo)
				goto err;

			output->gbm_cursor_fb[i] =
				drm_fb_get_from_bo(bo, device, false, BUFFER_CURSOR);
			if (!output->gbm_cursor_fb[i]) {
				gbm_bo_destroy(bo);
				goto err;
			}
			output->gbm_cursor_handle[i] = gbm_bo_get_handle(bo).s32;
		}
	}

	return 0;

err:
	weston_log("cursor buffers unavailable, using gl cursors\n");
	device->cursors_are_broken = true;
	drm_output_fini_cursor_egl(output);
	return -1;
}

static int
drm_output_init_cursor_vulkan(struct drm_output *output, struct drm_backend *b)
{
	struct drm_device *device = output->device;
	unsigned int i;

	/* No point creating cursors if we don't have a plane for them. */
	if (!output->cursor_plane)
		return 0;

	for (i = 0; i < ARRAY_LENGTH(output->gbm_cursor_fb); i++) {
		struct gbm_bo *bo;

		if (gbm_device_get_fd(b->gbm) != output->device->drm.fd) {
			output->gbm_cursor_fb[i] =
				drm_fb_create_dumb(output->device,
						   device->cursor_width,
						   device->cursor_height,
						   DRM_FORMAT_ARGB8888);
			/* Override buffer type, since we know it is a cursor */
			output->gbm_cursor_fb[i]->type = BUFFER_CURSOR;
			output->gbm_cursor_handle[i] =
				output->gbm_cursor_fb[i]->handles[0];
		} else {
			bo = gbm_bo_create(b->gbm, device->cursor_width, device->cursor_height,
					   GBM_FORMAT_ARGB8888,
					   GBM_BO_USE_CURSOR | GBM_BO_USE_WRITE);
			if (!bo)
				goto err;

			output->gbm_cursor_fb[i] =
				drm_fb_get_from_bo(bo, device, false, BUFFER_CURSOR);
			if (!output->gbm_cursor_fb[i]) {
				gbm_bo_destroy(bo);
				goto err;
			}
			output->gbm_cursor_handle[i] = gbm_bo_get_handle(bo).s32;
		}
	}

	return 0;

err:
	weston_log("cursor buffers unavailable, using vulkan cursors\n");
	device->cursors_are_broken = true;
	drm_output_fini_cursor_vulkan(output);
	return -1;
}

static void
create_gbm_surface(struct gbm_device *gbm, struct drm_output *output)
{
	struct weston_mode *mode = output->base.current_mode;
	struct drm_plane *plane = output->scanout_plane;
	struct weston_drm_format *fmt;
	const uint64_t *modifiers;
	unsigned int num_modifiers;

	fmt = weston_drm_format_array_find_format(&plane->formats,
						  output->format->format);
	if (!fmt) {
		weston_log("format %s not supported by output %s\n",
			   output->format->drm_format_name,
			   output->base.name);
		return;
	}

	if (!weston_drm_format_has_modifier(fmt, DRM_FORMAT_MOD_INVALID)) {
		modifiers = weston_drm_format_get_modifiers(fmt, &num_modifiers);
		output->gbm_surface =
			gbm_surface_create_with_modifiers(gbm,
							  mode->width, mode->height,
							  output->format->format,
							  modifiers, num_modifiers);
	}

	/*
	 * If we cannot use modifiers to allocate the GBM surface and the GBM
	 * device differs from the KMS display device (because we are rendering
	 * on a different GPU), we have to use linear buffers to make sure that
	 * the allocated GBM surface is correctly displayed on the KMS device.
	 */
	if (gbm_device_get_fd(gbm) != output->device->drm.fd)
		output->gbm_bo_flags |= GBM_BO_USE_LINEAR;

	/* We may allocate with no modifiers in the following situations:
	 *
	 * 1. the KMS driver does not support modifiers;
	 * 2. if allocating with modifiers failed, what can happen when the KMS
	 *    display device supports modifiers but the GBM driver does not,
	 *    e.g. the old i915 Mesa driver.
	 */
	if (!output->gbm_surface)
		output->gbm_surface = gbm_surface_create(gbm,
							 mode->width, mode->height,
							 output->format->format,
							 output->gbm_bo_flags);
}

enum format_alpha_required {
	FORMAT_ALPHA_REQUIRED = true,
	FORMAT_ALPHA_NOT_REQUIRED = false,
};

enum format_component_type {
	FORMAT_COMPONENT_TYPE_ANY,
	FORMAT_COMPONENT_TYPE_FLOAT_ONLY,
};

static const struct pixel_format_info *
find_compatible_format(struct weston_compositor *compositor,
		       struct wl_array *formats, int min_bpc,
		       enum format_component_type component_type,
		       enum format_alpha_required alpha_required)
{
	const struct pixel_format_info **tmp, *p;
	const struct pixel_format_info *candidate = NULL;

	/**
	 * Given a format array, this looks for a format respecting a few
	 * criteria. First of all, this ignores formats that do not contain an
	 * alpha channel when alpha_required == FORMAT_ALPHA_REQUIRED. Similar
	 * for formats that are not floating point when component_type ==
	 * FORMAT_COMPONENT_TYPE_FLOAT_ONLY. Also, it ignores formats that do
	 * not have bits per color channel (bpc) bigger or equal to min_bpc.
	 *
	 * When we have multiple formats matching these criteria, we use the
	 * following to choose:
	 *
	 * 1. a format with lower bytes per pixel (bpp) is favored.
	 *
	 * 2. if FORMAT_ALPHA_REQUIRED:
	 *	  we prefer the format with more bits on the alpha channel
	 *    else
	 *        we prefer the format with more bits on the color channels
	 */
	wl_array_for_each(tmp, formats) {
		p = *tmp;

		/* Skip candidates that do not match minimum criteria. */
		if (component_type == FORMAT_COMPONENT_TYPE_FLOAT_ONLY &&
		    p->component_type != PIXEL_COMPONENT_TYPE_FLOAT)
			continue;
		if (alpha_required == FORMAT_ALPHA_REQUIRED && p->bits.a == 0)
			continue;
		if (p->bits.r < min_bpc || p->bits.g < min_bpc || p->bits.b < min_bpc)
			continue;

		/* No other good candidate so far, so pick this one. */
		if (!candidate) {
			candidate = p;
			continue;
		}

		/**
		 * New candidate, let's compare with old and untie.
		 */

		if (p->bpp > candidate->bpp)
			continue;

		if (alpha_required == FORMAT_ALPHA_REQUIRED) {
			if (p->bits.a <= candidate->bits.a)
				continue;
		} else {
			if (p->bits.r + p->bits.g + p->bits.b <=
			    candidate->bits.r + candidate->bits.g + candidate->bits.b)
				continue;
		}

		candidate = p;
	}

	return candidate;
}

static bool
drm_output_pick_format_egl(struct drm_output *output)
{
	struct drm_device *device = output->device;
	struct drm_backend *b = device->backend;
	struct weston_compositor *compositor = b->compositor;
	const struct weston_renderer *renderer = compositor->renderer;
	const struct pixel_format_info **renderer_formats;
	const struct pixel_format_info **f;
	unsigned int renderer_formats_count;
	struct wl_array supported_formats;
	enum format_component_type component_type;
	uint32_t min_bpc;
	unsigned int i;
	bool ret = true;
	bool found;

	wl_array_init(&supported_formats);

	/**
	 * This computes the intersection between renderer formats supported by
	 * EGL and the output->scanout_plane supported formats. We need that as
	 * we want to select a format supported by both.
	 */
	renderer_formats =
		renderer->gl->get_supported_rendering_formats(b->compositor,
							      &renderer_formats_count);
	for (i = 0; i < renderer_formats_count; i++) {
		if (!weston_drm_format_array_find_format(&output->scanout_plane->formats,
							 renderer_formats[i]->format))
			continue;

		f = wl_array_add(&supported_formats, sizeof(*f));
		*f = renderer_formats[i];
	}

	if (output->base.from_blend_to_output_by_backend) {
		component_type = FORMAT_COMPONENT_TYPE_FLOAT_ONLY;
		min_bpc = 16;
	} else if (output->base.eotf_mode != WESTON_EOTF_MODE_SDR) {
		component_type = FORMAT_COMPONENT_TYPE_ANY;
		min_bpc = 10;
	} else {
		/**
		 * If no requirements, we simply use b->format instead of
		 * looking for a format with bpc >= min_bpc.
		 */
		min_bpc = 0;
	}

	if (min_bpc != 0) {
		if (b->has_underlay) {
			output->format =
				find_compatible_format(compositor, &supported_formats,
						       min_bpc, component_type,
						       FORMAT_ALPHA_REQUIRED);
			if (output->format)
				goto done;

			weston_log("Disabling underlay planes: EGL GBM or the primary plane for output '%s'\n" \
				   "does not support format with min bpc %u and alpha channel.\n",
				   output->base.name, min_bpc);
			b->has_underlay = false;
		}

		output->format =
			find_compatible_format(compositor, &supported_formats,
					       min_bpc, component_type,
					       FORMAT_ALPHA_NOT_REQUIRED);
		if (output->format)
			goto done;

		weston_log("Error: EGL GBM or the primary plane for output '%s' does not support format\n" \
			   "with min bpc %u.\n", output->base.name, min_bpc);
		ret = false;
		goto done;
	}

	found = false;
	wl_array_for_each(f, &supported_formats) {
		if ((*f)->format == b->format->format) {
			found = true;
			break;
		}
	}
	if (!found) {
		weston_log("Error: format %s unsupported by EGL GBM or the primary plane for output '%s'.\n",
			   b->format->drm_format_name, output->base.name);
		ret = false;
		goto done;
	}

	if (b->has_underlay && (b->format->bits.a == 0)) {
		weston_log("Disabling underlay planes: b->format %s does not have alpha channel,\n"
			   "which is required to support underlay planes.\n",
			   b->format->drm_format_name);
		b->has_underlay = false;
	}

	output->format = b->format;

done:
	wl_array_release(&supported_formats);
	return ret;
}

/* Init output state that depends on gl or gbm */
int
drm_output_init_egl(struct drm_output *output, struct drm_backend *b)
{
	const struct weston_renderer *renderer = b->compositor->renderer;
	const struct weston_mode *mode = output->base.current_mode;
	const struct pixel_format_info *format[2] = { 0 };
	struct gl_renderer_output_options options;

	if (!output->format && !drm_output_pick_format_egl(output))
		return -1;

	format[0] = output->format;
	if (!b->has_underlay)
		format[1] = fallback_format_for(output->format);

	options.formats = format;
	options.formats_count = format[1] ? 2 : 1;
	options.area.x = 0;
	options.area.y = 0;
	options.area.width = mode->width;
	options.area.height = mode->height;
	options.fb_size.width = mode->width;
	options.fb_size.height = mode->height;

	assert(output->gbm_surface == NULL);
	create_gbm_surface(b->gbm, output);
	if (!output->gbm_surface) {
		weston_log("failed to create gbm surface\n");
		return -1;
	}

	options.window_for_legacy = (EGLNativeWindowType) output->gbm_surface;
	options.window_for_platform = output->gbm_surface;
	if (renderer->gl->output_window_create(&output->base, &options) < 0) {
		weston_log("failed to create gl renderer output state\n");
		gbm_surface_destroy(output->gbm_surface);
		output->gbm_surface = NULL;
		return -1;
	}

	drm_output_init_cursor_egl(output, b);

	return 0;
}

static void
create_gbm_bos(struct gbm_device *gbm, struct drm_output *output, unsigned int n)
{
	struct weston_mode *mode = output->base.current_mode;
	struct drm_plane *plane = output->scanout_plane;
	struct weston_drm_format *fmt;
	const uint64_t *modifiers;
	unsigned int num_modifiers;

	fmt = weston_drm_format_array_find_format(&plane->formats,
						  output->format->format);
	if (!fmt) {
		weston_log("format %s not supported by output %s\n",
			   output->format->drm_format_name,
			   output->base.name);
		return;
	}

	if (!weston_drm_format_has_modifier(fmt, DRM_FORMAT_MOD_INVALID)) {
		modifiers = weston_drm_format_get_modifiers(fmt, &num_modifiers);
		for (unsigned int i = 0; i < n; i++) {
			output->gbm_bos[i] =
				gbm_bo_create_with_modifiers(gbm,
							     mode->width, mode->height,
							     output->format->format,
							     modifiers, num_modifiers);
		}
	}

	/*
	 * If we cannot use modifiers to allocate the GBM surface and
	 * the GBM device differs from the KMS display device, try to
	 * use linear buffers and hope that the allocated GBM surface
	 * is correctly displayed on the KMS device.
	 */
	if (gbm_device_get_fd(gbm) != output->device->drm.fd)
		output->gbm_bo_flags |= GBM_BO_USE_LINEAR;

	if (!output->gbm_bos[0]) {
		for (unsigned int i = 0; i < n; i++) {
			output->gbm_bos[i] = gbm_bo_create(gbm,
							   mode->width, mode->height,
							   output->format->format,
							   output->gbm_bo_flags);
		}
	}

	struct drm_device *device = output->device;
	for (unsigned int i = 0; i < n; i++) {
		assert(output->gbm_bos[i]);
		drm_fb_get_from_bo(output->gbm_bos[i], device, !output->format->opaque_substitute,
				   BUFFER_GBM_BO);
	}

	assert(output->gbm_surface == NULL);
}

/* Init output state that depends on vulkan or gbm */
int
drm_output_init_vulkan(struct drm_output *output, struct drm_backend *b)
{
	const struct weston_renderer *renderer = b->compositor->renderer;
	const struct weston_mode *mode = output->base.current_mode;
	const struct pixel_format_info *format[2] = {
		output->format,
		fallback_format_for(output->format),
	};
	struct vulkan_renderer_output_options options = {
		.formats = format,
		.formats_count = 1,
		.area.x = 0,
		.area.y = 0,
		.area.width = mode->width,
		.area.height = mode->height,
		.fb_size.width = mode->width,
		.fb_size.height = mode->height,
	};

	assert(output->gbm_surface == NULL);

	/*
	 * TODO: This method for BO allocation needs to be reworked.
	 * Currently, it allocates a buffer based on the list of acceptable
	 * modifiers received from the DRM backend but does not check it
	 * against formats renderable by the renderer (and there is no
	 * straightforward way to do so yet).
	 * Most likely this should be replaced by sending the acceptable
	 * modifiers list from the DRM backend to the renderer and doing the
	 * optimal dmabuf allocation in the renderer. But as of this writing,
	 * this API for dmabuf allocation is not yet implemented in the
	 * Vulkan renderer.
	 */
	create_gbm_bos(b->gbm, output, NUM_GBM_BOS);
	if (!output->gbm_bos[0]) {
		weston_log("failed to create gbm bos\n");
		return -1;
	}
	options.num_gbm_bos = NUM_GBM_BOS;

	if (options.formats[1])
		options.formats_count = 2;

	for (unsigned int i = 0; i < options.num_gbm_bos; i++)
		options.gbm_bos[i] = output->gbm_bos[i];

	if (renderer->vulkan->output_window_create(&output->base, &options) < 0) {
		weston_log("failed to create vulkan renderer output state\n");
		gbm_surface_destroy(output->gbm_surface);
		output->gbm_surface = NULL;
		return -1;
	}

	drm_output_init_cursor_vulkan(output, b);

	return 0;
}

void
drm_output_fini_egl(struct drm_output *output)
{
	struct drm_backend *b = output->backend;
	const struct weston_renderer *renderer = b->compositor->renderer;

	/* Destroying the GBM surface will destroy all our GBM buffers,
	 * regardless of refcount. Ensure we destroy them here. */
	if (!b->compositor->shutting_down &&
	    output->scanout_plane->state_cur->fb &&
	    output->scanout_plane->state_cur->fb->type == BUFFER_GBM_SURFACE) {
		drm_plane_reset_state(output->scanout_plane);
	}

	renderer->gl->output_destroy(&output->base);
	gbm_surface_destroy(output->gbm_surface);
	output->gbm_surface = NULL;
	drm_output_fini_cursor_egl(output);
}

void
drm_output_fini_vulkan(struct drm_output *output)
{
	struct drm_backend *b = output->backend;
	const struct weston_renderer *renderer = b->compositor->renderer;

	/* Destroying the GBM surface will destroy all our GBM buffers,
	 * regardless of refcount. Ensure we destroy them here. */
	if (!b->compositor->shutting_down &&
	    output->scanout_plane->state_cur->fb &&
	    output->scanout_plane->state_cur->fb->type == BUFFER_GBM_BO) {
		drm_plane_reset_state(output->scanout_plane);
	}

	renderer->vulkan->output_destroy(&output->base);
	for (unsigned int i = 0; i < NUM_GBM_BOS; i++)
		gbm_bo_destroy(output->gbm_bos[i]);
	output->gbm_surface = NULL;
	drm_output_fini_cursor_vulkan(output);
}

struct drm_fb *
drm_output_render_gl(struct drm_output_state *state, pixman_region32_t *damage)
{
	struct drm_output *output = state->output;
	struct drm_device *device = output->device;
	struct gbm_bo *bo;
	struct drm_fb *ret;

	output->base.compositor->renderer->repaint_output(&output->base,
							  damage, NULL);

	bo = gbm_surface_lock_front_buffer(output->gbm_surface);
	if (!bo) {
		weston_log("failed to lock front buffer: %s\n",
			   strerror(errno));
		return NULL;
	}

	/* Output transparent/opaque image according to the format required by
	 * the client. */
	ret = drm_fb_get_from_bo(bo, device, !output->format->opaque_substitute,
	                         BUFFER_GBM_SURFACE);
	if (!ret) {
		weston_log("failed to get drm_fb for bo\n");
		gbm_surface_release_buffer(output->gbm_surface, bo);
		return NULL;
	}
	ret->gbm_surface = output->gbm_surface;

	return ret;
}

struct drm_fb *
drm_output_render_vulkan(struct drm_output_state *state, pixman_region32_t *damage)
{
	struct drm_output *output = state->output;
	struct drm_device *device = output->device;
	struct gbm_bo *bo;
	struct drm_fb *ret;

	output->base.compositor->renderer->repaint_output(&output->base,
							  damage, NULL);

	bo = output->gbm_bos[output->current_bo];
	if (!bo) {
		weston_log("failed to get gbm_bo\n");
		return NULL;
	}

	/* Output transparent/opaque image according to the format required by
	 * the client. */
	ret = drm_fb_get_from_bo(bo, device, !output->format->opaque_substitute,
	                         BUFFER_GBM_BO);
	if (!ret) {
		weston_log("failed to get drm_fb for bo\n");
		return NULL;
	}
	ret->bo = bo;

	ret->gbm_surface = NULL;
	output->current_bo = (output->current_bo + 1) % NUM_GBM_BOS;

	return ret;
}
