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

// uniform vec3 wspos_camera;
// in vec3 vtx_pos;


// uniform struct {
//     sampler2D data_texture;
//     sampler2D heightfield;
//     int view_index;
//     int terrain_size;
//     int chunk_size;
// } ShaderTerrainMesh;



// Compute normal from the heightmap
// vec3 get_terrain_normal() {
//     const float terrain_height = 50.0;
//     // vec3 pixel_size = vec3(1.0, -1.0, 0) / textureSize(ShaderTerrainMesh.heightfield, 0).xxx;
//     vec3 pixel_size = vec3(1.0, -1.0, 0) / vertex.xxx;
//     float u0 = texture(ShaderTerrainMesh.heightfield, vertex.xy + pixel_size.yz).x * terrain_height;
//     float u1 = texture(ShaderTerrainMesh.heightfield, vertex.xy + pixel_size.xz).x * terrain_height;
//     float v0 = texture(ShaderTerrainMesh.heightfield, vertex.xy + pixel_size.zy).x * terrain_height;
//     float v1 = texture(ShaderTerrainMesh.heightfield, vertex.xy + pixel_size.zx).x * terrain_height;

//     // float u0 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.yz).x * terrain_height;
//     // float u1 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.xz).x * terrain_height;
//     // float v0 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.zy).x * terrain_height;
//     // float v1 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.zx).x * terrain_height;
//     vec3 tangent = normalize(vec3(1.0, 0, u1 - u0));
//     vec3 binormal = normalize(vec3(0, 1.0, v1 - v0));
//     return normalize(cross(tangent, binormal));
// }


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
    
    float w = tex_g.r;
    vec3 ground = tex4.rgb * w + tex3 * (1.0 - w);
    vec3 color = vertex.z <= 0.0 ? ground: diffuse;

    // vec3 normal = get_terrain_normal();
    // vec3 fake_sun = normalize(vec3(0.7, 0.2, 0.6));
    // vec3 shading = max(0.0, dot(normal, fake_sun)) * color;
    // shading += vec3(0.07, 0.07, 0.1); 
    // fragColor = vec4(shading, 1.0);
    
    // fake fog
    // float dist = distance(vtx_pos, wspos_camera);
    // float fog_factor = smoothstep(0.0, 1.0, dist/1000.0);
    // color = mix(color, vec3(0.7, 0.7, 0.8), fog_factor);


    fragColor = vec4(color, 1.0);

    if (vertex.z > 0.0 && vertex.z < 0.1 && tex_g.r > 0.2) {
        discard;
    }
}