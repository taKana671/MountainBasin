#version 300 es
precision highp float;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;
in vec4 p3d_Normal;

in vec2 p3d_MultiTexCoord0;
in vec2 p3d_MultiTexCoord1;
in vec2 p3d_MultiTexCoord2;
in vec2 p3d_MultiTexCoord3;
in vec2 p3d_MultiTexCoord4;
in vec2 p3d_MultiTexCoord5;

out vec2 texcoord0;
out vec2 texcoord1;
out vec2 texcoord2;
out vec2 texcoord3;
out vec2 texcoord4;
out vec2 texcoord_g;
out vec4 vertex;

// out vec3 vtx_pos;
// out vec2 terrain_uv;
// uniform struct {
//     sampler2D data_texture;
//     sampler2D heightfield;
//     int view_index;
//     int terrain_size;
//     int chunk_size;
// } ShaderTerrainMesh;

// https://discourse.panda3d.org/t/shader-terrain-normal-mapping-fails-for-a-new-buffer/29713/4

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord0 = p3d_MultiTexCoord0;
    texcoord1 = p3d_MultiTexCoord1;
    texcoord2 = p3d_MultiTexCoord2;
    texcoord3 = p3d_MultiTexCoord3;
    texcoord4 = p3d_MultiTexCoord4;

    texcoord_g = p3d_MultiTexCoord5;
    vertex = p3d_Vertex;

    // // vtx_pos = (p3d_ModelMatrix * vec4(vertex.xyz, 1)).xyz;

    //  vec4 terrain_data = texelFetch(ShaderTerrainMesh.data_texture,
    // ivec2(gl_InstanceID, ShaderTerrainMesh.view_index), 0);

    // // Get initial chunk position in the (0, 0, 0), (1, 1, 0) range
    // vec3 chunk_position = p3d_Vertex.xyz;

    // // CLOD implementation
    // float clod_factor = smoothstep(0.0, 1.0, terrain_data.w);
    // chunk_position.xy -= clod_factor * fract(chunk_position.xy * float(ShaderTerrainMesh.chunk_size) / 2.0)
    //                         * 2.0 / float(ShaderTerrainMesh.chunk_size);

    // // // Scale the chunk
    // // chunk_position *= terrain_data.z * float(ShaderTerrainMesh.chunk_size)
    // //                     / float(ShaderTerrainMesh.terrain_size);
    // // chunk_position.z *= ShaderTerrainMesh.chunk_size;

    // // // Offset the chunk, it is important that this happens after the scale
    // // chunk_position.xy += terrain_data.xy / float(ShaderTerrainMesh.terrain_size);

    // // Scale the chunk
    // chunk_position *= terrain_data.z * float(ShaderTerrainMesh.chunk_size)
    //                     / float(ShaderTerrainMesh.terrain_size);
    // chunk_position.z *= float(ShaderTerrainMesh.chunk_size);

    // // Offset the chunk, it is important that this happens after the scale
    // chunk_position.xy += terrain_data.xy / float(ShaderTerrainMesh.terrain_size);


    // // Compute the terrain UV coordinates
    // terrain_uv = chunk_position.xy;

    // // Sample the heightfield and offset the terrain - we do not need to multiply
    // // the height with anything since the terrain transform is included in the
    // // model view projection matrix.
    // chunk_position.z += texture(ShaderTerrainMesh.heightfield, terrain_uv).x;
    // gl_Position = p3d_ModelViewProjectionMatrix * vec4(chunk_position, 1);

    // // Output the vertex world space position - in this case we use this to render
    // // the fog.
    // vtx_pos = (p3d_ModelMatrix * vec4(chunk_position, 1)).xyz;
}



