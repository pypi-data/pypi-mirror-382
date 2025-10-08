/*
 * Copyright 2012 Intel Corporation
 * Copyright 2015,2019,2021 Collabora, Ltd.
 * Copyright 2016 NVIDIA Corporation
 * Copyright 2021 Advanced Micro Devices, Inc.
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

/* GLSL version 1.00 ES, defined in gl-shaders.c */

/* For annotating shader compile-time constant arguments */
#define compile_const const

/*
 * Enumeration of shader variants, must match enum gl_shader_texture_variant.
 */
#define SHADER_VARIANT_RGBA     1
#define SHADER_VARIANT_Y_U_V    2
#define SHADER_VARIANT_Y_UV     3
#define SHADER_VARIANT_XYUV     4
#define SHADER_VARIANT_SOLID    5
#define SHADER_VARIANT_EXTERNAL 6

/* enum gl_shader_color_curve */
#define SHADER_COLOR_CURVE_IDENTITY 0
#define SHADER_COLOR_CURVE_LUT_3x1D 1
#define SHADER_COLOR_CURVE_LINPOW 2
#define SHADER_COLOR_CURVE_POWLIN 3
#define SHADER_COLOR_CURVE_PQ 4
#define SHADER_COLOR_CURVE_PQ_INVERSE 5

/* enum gl_shader_color_mapping */
#define SHADER_COLOR_MAPPING_IDENTITY 0
#define SHADER_COLOR_MAPPING_3DLUT 1
#define SHADER_COLOR_MAPPING_MATRIX 2

#if DEF_VARIANT == SHADER_VARIANT_EXTERNAL
#extension GL_OES_EGL_image_external : require
#endif

#if DEF_COLOR_MAPPING == SHADER_COLOR_MAPPING_3DLUT
#extension GL_OES_texture_3D : require
#endif

#ifdef GL_FRAGMENT_PRECISION_HIGH
#define HIGHPRECISION highp
#else
#define HIGHPRECISION mediump
#endif

precision HIGHPRECISION float;

/*
 * These undeclared identifiers will be #defined by a runtime generated code
 * snippet.
 */
compile_const int c_variant = DEF_VARIANT;
compile_const int c_color_pre_curve = DEF_COLOR_PRE_CURVE;
compile_const int c_color_mapping = DEF_COLOR_MAPPING;
compile_const int c_color_post_curve = DEF_COLOR_POST_CURVE;

compile_const bool c_input_is_premult = DEF_INPUT_IS_PREMULT;
compile_const bool c_tint = DEF_TINT;
compile_const bool c_wireframe = DEF_WIREFRAME;
compile_const bool c_need_color_pipeline =
	c_color_pre_curve != SHADER_COLOR_CURVE_IDENTITY ||
	c_color_mapping != SHADER_COLOR_MAPPING_IDENTITY ||
	c_color_post_curve != SHADER_COLOR_CURVE_IDENTITY;

vec4
yuva2rgba(vec4 yuva)
{
	vec4 color_out;
	float Y, su, sv;

	/* ITU-R BT.601 & BT.709 quantization (limited range) */

	Y = 255.0/219.0 * (yuva.x - 16.0/255.0);

	/* Remove offset 128/255, but the 255/224 multiplier comes later */
	su = yuva.y - 128.0/255.0;
	sv = yuva.z - 128.0/255.0;

	/*
	 * ITU-R BT.709 encoding coefficients (inverse), with the
	 * 255/224 limited range multiplier already included in the
	 * factors for su (Cb) and sv (Cr).
	 */
	color_out.r = Y                   + 1.79274107 * sv;
	color_out.g = Y - 0.21324861 * su - 0.53290933 * sv;
	color_out.b = Y + 2.11240179 * su;

	color_out.a = yuva.w;

	return color_out;
}

#if DEF_VARIANT == SHADER_VARIANT_EXTERNAL
uniform samplerExternalOES tex;
#else
uniform sampler2D tex;
#endif

varying HIGHPRECISION vec2 v_texcoord;
varying HIGHPRECISION vec4 v_color;
varying HIGHPRECISION vec3 v_barycentric;

uniform sampler2D tex1;
uniform sampler2D tex2;
uniform sampler2D tex_wireframe;
uniform float view_alpha;
uniform vec4 unicolor;
uniform vec4 tint;
uniform ivec4 swizzle_idx[3];
uniform vec4 swizzle_mask[3];
uniform vec4 swizzle_sub[3];

/* #define MAX_CURVE_PARAMS is runtime generated. */
#define MAX_CURVESET_PARAMS (MAX_CURVE_PARAMS * 3)

struct lut_2d_t {
	HIGHPRECISION sampler2D lut_2d;
	HIGHPRECISION vec2 scale_offset;
};

struct parametric_curve_t {
	HIGHPRECISION float params[MAX_CURVESET_PARAMS];
	bool clamped_input;
};

uniform lut_2d_t color_pre_curve_lut;
uniform parametric_curve_t color_pre_curve_par;

uniform lut_2d_t color_post_curve_lut;
uniform parametric_curve_t color_post_curve_par;

#if DEF_COLOR_MAPPING == SHADER_COLOR_MAPPING_3DLUT
uniform HIGHPRECISION sampler3D color_mapping_lut_3d;
uniform HIGHPRECISION vec2 color_mapping_lut_scale_offset;
#endif
uniform HIGHPRECISION mat3 color_mapping_matrix;
uniform HIGHPRECISION vec3 color_mapping_offset;

/*
 * 2D texture sampler abstracting away the lack of swizzles on OpenGL ES 2. This
 * should only be used by code relying on swizzling. 'unit' is the texture unit
 * used to index the swizzling uniforms, which must appropriately be set prior
 * to draw call.
 */
vec4
texture2D_swizzle(sampler2D sampler, int unit, vec2 coord)
{
#if GLES_API_MAJOR_VERSION == 3
	return texture2D(sampler, coord);
#else
	vec4 color = texture2D(sampler, coord);

	/* Swizzle components. */
	color = vec4(color[swizzle_idx[unit].x],
		     color[swizzle_idx[unit].y],
		     color[swizzle_idx[unit].z],
		     color[swizzle_idx[unit].w]);

	/* Substitute with 0 or 1. */
	return color * swizzle_mask[unit] + swizzle_sub[unit];
#endif
}

#if DEF_VARIANT == SHADER_VARIANT_EXTERNAL
vec4
texture2D_swizzle(samplerExternalOES sampler, int unit, vec2 coord)
{
	return texture2D(sampler, coord);
}
#endif

vec4
sample_input_texture()
{
	vec4 yuva = vec4(0.0, 0.0, 0.0, 1.0);

	/* Producing RGBA directly */

	if (c_variant == SHADER_VARIANT_SOLID)
		return unicolor;

	if (c_variant == SHADER_VARIANT_EXTERNAL ||
	    c_variant == SHADER_VARIANT_RGBA)
		return texture2D_swizzle(tex, 0, v_texcoord);

	/* Requires conversion to RGBA */

	if (c_variant == SHADER_VARIANT_Y_U_V) {
		yuva.x = texture2D_swizzle(tex, 0, v_texcoord).r;
		yuva.y = texture2D_swizzle(tex1, 1, v_texcoord).r;
		yuva.z = texture2D_swizzle(tex2, 2, v_texcoord).r;

	} else if (c_variant == SHADER_VARIANT_Y_UV) {
		yuva.x = texture2D_swizzle(tex, 0, v_texcoord).r;
		yuva.yz = texture2D_swizzle(tex1, 1, v_texcoord).rg;

	} else if (c_variant == SHADER_VARIANT_XYUV) {
		yuva.xyz = texture2D_swizzle(tex, 0, v_texcoord).rgb;

	} else {
		/* Never reached, bad variant value. */
		return vec4(1.0, 0.3, 1.0, 1.0);
	}

	return yuva2rgba(yuva);
}

/*
 * Sample a 1D LUT which is a single row of a 2D texture. The 2D texture has
 * four rows so that the centers of texels have precise y-coordinates.
 *
 * Texture coordinates go from 0.0 to 1.0 corresponding to texture edges.
 * When we do LUT look-ups with linear filtering, the correct range to sample
 * from is not from edge to edge, but center of first texel to center of last
 * texel. This follows because with LUTs, you have the exact end points given,
 * you never extrapolate but only interpolate.
 * The scale and offset are precomputed to achieve this mapping.
 */
float
sample_lut_1d(const lut_2d_t lut, float x, compile_const int row)
{
	float tx = x * lut.scale_offset.s + lut.scale_offset.t;
	float ty = (float(row) + 0.5) / 4.0;

	return texture2D(lut.lut_2d, vec2(tx, ty)).x;
}

vec3
sample_lut_3x1d(const lut_2d_t lut, vec3 color)
{
	return vec3(sample_lut_1d(lut, color.r, 0),
		    sample_lut_1d(lut, color.g, 1),
		    sample_lut_1d(lut, color.b, 2));
}

vec3
lut_texcoord(vec3 pos, vec2 scale_offset)
{
	return pos * scale_offset.s + scale_offset.t;
}

struct gabcd_t {
	float g, a, b, c, d;
	bool clamp;
};

gabcd_t
unpack_params(const parametric_curve_t par, compile_const int chan)
{
	/*
	 * For each color channel we have MAX_CURVE_PARAMS parameters.
	 * The parameters for the three curves are stored in RGB order.
	 */
	return gabcd_t(
		par.params[0 + chan * MAX_CURVE_PARAMS],
		par.params[1 + chan * MAX_CURVE_PARAMS],
		par.params[2 + chan * MAX_CURVE_PARAMS],
		par.params[3 + chan * MAX_CURVE_PARAMS],
		par.params[4 + chan * MAX_CURVE_PARAMS],
		par.clamped_input
	);
}

float
linpow(float x, const gabcd_t p)
{
	/* See WESTON_COLOR_CURVE_PARAMETRIC_TYPE_LINPOW for details about LINPOW. */

	if (x >= p.d)
		return pow((p.a * x) + p.b, p.g);

	return p.c * x;
}

float
sample_linpow(const gabcd_t p, float x)
{
	if (p.clamp)
		x = clamp(x, 0.0, 1.0);

	/* We use mirroring for negative input values. */
	if (x < 0.0)
		return -linpow(-x, p);

	return linpow(x, p);
}

vec3
sample_linpow_vec3(const parametric_curve_t par, vec3 color)
{
	return vec3(sample_linpow(unpack_params(par, 0), color.r),
		    sample_linpow(unpack_params(par, 1), color.g),
		    sample_linpow(unpack_params(par, 2), color.b));
}

float
powlin(float x, const gabcd_t p)
{
	/* See WESTON_COLOR_CURVE_PARAMETRIC_TYPE_POWLIN for details about POWLIN. */

	if (x >= p.d)
		return p.a * pow(x, p.g) + p.b;

	return p.c * x;
}

float
sample_powlin(const gabcd_t p, float x)
{
	if (p.clamp)
		x = clamp(x, 0.0, 1.0);

	/* We use mirroring for negative input values. */
	if (x < 0.0)
		return -powlin(-x, p);

	return powlin(x, p);
}

vec3
sample_powlin_vec3(const parametric_curve_t par, vec3 color)
{
	return vec3(sample_powlin(unpack_params(par, 0), color.r),
		    sample_powlin(unpack_params(par, 1), color.g),
		    sample_powlin(unpack_params(par, 2), color.b));
}

float
perceptual_quantizer(float x)
{
	float aux, c1, c2, c3, m1_inv, m2_inv;

	m1_inv = 1.0 / 0.1593017578125;
	m2_inv = 1.0 / 78.84375;
	c1 = 0.8359375;
	c2 = 18.8515625;
	c3 = 18.6875;
	aux = pow(x, m2_inv);

	/* Normalized result. We don't take into consideration the luminance
	 * levels, as that's only useful when converting the optical values to
	 * nits, but we return them in the [0, 1] range. */
	return pow(max(aux - c1, 0.0) / (c2 - c3 * aux), m1_inv);
}

float
perceptual_quantizer_inverse(float x)
{
	float aux, c1, c2, c3, m1, m2;

	m1 = 0.1593017578125;
	m2 = 78.84375;
	c1 = 0.8359375;
	c2 = 18.8515625;
	c3 = 18.6875;
	aux = pow(x, m1);

	/* Normalized result. We don't take into consideration the luminance
	 * levels, as we don't receive the input as nits, but normalized in the
	 * [0, 1] range. */
	return pow((c1 + c2 * aux) / (1.0 + c3 * aux), m2);
}

float
sample_perceptual_quantizer(compile_const bool inverse, float x)
{
	/* PQ and its inverse are only defined for input values in this range. */
	x = clamp(x, 0.0, 1.0);

	if (inverse)
		return perceptual_quantizer_inverse(x);

	return perceptual_quantizer(x);
}

vec3
sample_perceptual_quantizer_vec3(compile_const bool inverse, vec3 color)
{
	return vec3(sample_perceptual_quantizer(inverse, color.r),
		    sample_perceptual_quantizer(inverse, color.g),
		    sample_perceptual_quantizer(inverse, color.b));
}

vec3
color_curve(compile_const int curve_type,
	    const lut_2d_t lut,
	    const parametric_curve_t par,
	    vec3 color)
{
	if (curve_type == SHADER_COLOR_CURVE_IDENTITY) {
		return color;
	} else if (curve_type == SHADER_COLOR_CURVE_LUT_3x1D) {
		return sample_lut_3x1d(lut, color);
	} else if (curve_type == SHADER_COLOR_CURVE_LINPOW) {
		return sample_linpow_vec3(par, color);
	} else if (curve_type == SHADER_COLOR_CURVE_POWLIN) {
		return sample_powlin_vec3(par, color);
	} else if (curve_type == SHADER_COLOR_CURVE_PQ) {
		return sample_perceptual_quantizer_vec3(false, /* not inverse */
							color);
	} else if (curve_type == SHADER_COLOR_CURVE_PQ_INVERSE) {
		return sample_perceptual_quantizer_vec3(true, /* inverse */
							color);
	} else {
		/* Never reached, bad c_color_pre_curve. */
		return vec3(1.0, 0.3, 1.0);
	}
}

vec3
sample_color_mapping_lut_3d(vec3 color)
{
	vec3 pos, ret = vec3(0.0, 0.0, 0.0);
#if DEF_COLOR_MAPPING == SHADER_COLOR_MAPPING_3DLUT
	pos = lut_texcoord(color, color_mapping_lut_scale_offset);
	ret = texture3D(color_mapping_lut_3d, pos).rgb;
#endif
	return ret;
}

vec3
color_mapping(vec3 color)
{
	if (c_color_mapping == SHADER_COLOR_MAPPING_IDENTITY)
		return color;
	else if (c_color_mapping == SHADER_COLOR_MAPPING_3DLUT)
		return sample_color_mapping_lut_3d(color);
	else if (c_color_mapping == SHADER_COLOR_MAPPING_MATRIX)
		return color_mapping_matrix * color.rgb + color_mapping_offset;
	else /* Never reached, bad c_color_mapping. */
		return vec3(1.0, 0.3, 1.0);
}

vec4
color_pipeline(vec4 color)
{
	/* Ensure straight alpha */
	if (c_input_is_premult) {
		if (color.a == 0.0)
			color.rgb = vec3(0, 0, 0);
		else
			color.rgb *= 1.0 / color.a;
	}

	color.rgb = color_curve(c_color_pre_curve, color_pre_curve_lut,
				color_pre_curve_par, color.rgb);
	color.rgb = color_mapping(color.rgb);
	color.rgb = color_curve(c_color_post_curve, color_post_curve_lut,
				color_post_curve_par, color.rgb);

	return color;
}

vec4
wireframe()
{
	float edge1 = texture2D(tex_wireframe, vec2(v_barycentric.x, 0.5)).r;
	float edge2 = texture2D(tex_wireframe, vec2(v_barycentric.y, 0.5)).r;
	float edge3 = texture2D(tex_wireframe, vec2(v_barycentric.z, 0.5)).r;

	return vec4(clamp(edge1 + edge2 + edge3, 0.0, 1.0));
}

void
main()
{
	vec4 color;

	/* Electrical (non-linear) RGBA values, may be premult or not */
	color = sample_input_texture();

	if (c_need_color_pipeline)
		color = color_pipeline(color); /* Produces straight alpha */

	/* Ensure pre-multiplied for blending */
	if (!c_input_is_premult || c_need_color_pipeline)
		color.rgb *= color.a;

	color *= view_alpha;

	if (c_tint)
		color = color * vec4(1.0 - tint.a) + tint;

	if (c_wireframe) {
		vec4 src = wireframe();
		color = color * vec4(1.0 - src.a) + src;
	}

	gl_FragColor = color;
}
