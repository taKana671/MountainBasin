#version 300 es
precision highp float;

uniform float tex_ScaleFactor0;
uniform float tex_ScaleFactor1;
uniform float tex_ScaleFactor2;
uniform float tex_ScaleFactor3;
uniform float tex_ScaleFactor4;

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;
uniform sampler2D p3d_Texture4;
uniform sampler2D p3d_Texture5;
uniform sampler2D tex_attribute;

in vec2 texcoord0;
in vec2 texcoord1;
in vec2 texcoord2;
in vec2 texcoord3;
in vec2 texcoord4;
in vec2 texcoord_g;
in vec4 vertex;

out vec4 fragColor;


void main() {
    // tex_rock
    vec3 tex0 = texture(p3d_Texture0, texcoord0.st * tex_ScaleFactor0).rgb;
    // tex_grass
    vec3 tex1 = texture(p3d_Texture1, texcoord1.st * tex_ScaleFactor1).rgb;
    // tex_crackes
    vec3 tex2 = texture(p3d_Texture2, texcoord2.st * tex_ScaleFactor2).rgb;
    // tex_moss
    vec3 tex3 = texture(p3d_Texture3, texcoord3.st * tex_ScaleFactor3).rgb;
    // tex_ground_rock
    vec3 tex4 = texture(p3d_Texture4, texcoord4.st * tex_ScaleFactor4).rgb;

    vec3 diffuse = tex1 * texture(tex_attribute, texcoord1.st).r;
    diffuse += tex2 * texture(tex_attribute, texcoord2.st).g;
    diffuse += tex0 * texture(tex_attribute, texcoord0.st).b;
    diffuse += tex3 * texture(tex_attribute, texcoord3.st).a;

    vec4 tex_g = texture(p3d_Texture5, texcoord_g.st).rgba;
    fragColor = vec4(diffuse, 1.0);

    if ((vertex.z <= 0.0) || (vertex.z > 0.0 && vertex.z < 0.1 && tex_g.r > 0.2)) {
        discard;
    }
}