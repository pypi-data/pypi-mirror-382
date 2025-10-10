// Cytosim was created by Francois Nedelec. Copyright 2021 Cambridge University

#ifndef SIMD_PRINT_H
#define SIMD_PRINT_H

// Functions to print SIMD vectors

#include <cstdio>

// restrict functions to local scope
#define LOCAL static inline

// printf code for a string:
#define STG_F "%10s "

// printf code for a float:
#define FLT_F "%9.6f "

//---------------------------------- SSE ---------------------------------------

#if USE_SIMD

/// print SIMD vector of 2 doubles
LOCAL void dump(vec2 v, char const* s, char end='\n')
{
    printf(STG_F "d( " FLT_F FLT_F ")%c", s, v[1], v[0], end);
}

/// print two SIMD vector
LOCAL void dump(vec2 v, vec2 w, char const* s, char end='\n')
{
    printf(STG_F "d( " FLT_F FLT_F ")( " FLT_F FLT_F ")%c", s, v[1], v[0], w[1], w[0], end);
}

/// print SIMD vector of 4 floats
LOCAL void dump(vec2f v, char const* s, char end='\n')
{
    printf(STG_F "f( " FLT_F FLT_F ")%c", s, v[1], v[0], end);
}

#if !defined(__SSE3__)
/// print SIMD vector of 4 floats
LOCAL void dump(vec4f v, char const* s, char end='\n')
{
    printf(STG_F "f( " FLT_F FLT_F FLT_F FLT_F ")%c", s, v[3], v[2], v[1], v[0], end);
}
#endif

/// print two SIMD vector of 4 floats
LOCAL void dump(vec4f x, vec4f y, char const* s, char end='\n')
{
    printf(STG_F "f( " FLT_F FLT_F ")( " FLT_F FLT_F ")( " FLT_F FLT_F ")( " FLT_F FLT_F ")%c", s, x[3], y[3], x[2], y[2], x[1], y[1], x[0], y[0], end);
}

#endif

//------------------------------- INTEGERS -------------------------------------

#ifdef __SSE3__

LOCAL void dump16(__m128i v, char const* s, char end='\n')
{
    uint16_t a = _mm_extract_epi16(v, 0);
    uint16_t b = _mm_extract_epi16(v, 1);
    uint16_t c = _mm_extract_epi16(v, 2);
    uint16_t d = _mm_extract_epi16(v, 3);
    uint16_t e = _mm_extract_epi16(v, 4);
    uint16_t f = _mm_extract_epi16(v, 5);
    uint16_t g = _mm_extract_epi16(v, 6);
    uint16_t h = _mm_extract_epi16(v, 7);
    printf(STG_F " int16( %3i %3i %3i %3i %3i %3i %3i %3i )%c", s, h, g, f, e, d, c, b, a, end);
}

LOCAL void dump32(__m128i v, char const* s, char end='\n')
{
    uint32_t a = _mm_extract_epi32(v, 0);
    uint32_t b = _mm_extract_epi32(v, 1);
    uint32_t c = _mm_extract_epi32(v, 2);
    uint32_t d = _mm_extract_epi32(v, 3);
    printf(STG_F " int32( %5i %5i %5i %5i )%c", s, d, c, b, a, end);
}

#endif

//---------------------------------- AVX ---------------------------------------

#ifdef __AVX__

/// print SIMD vector of 4 doubles
LOCAL void dump(vec4 v, char const* s, char end='\n')
{
    printf(STG_F "d( " FLT_F FLT_F FLT_F FLT_F " )%c", s, v[3], v[2], v[1], v[0], end);
}

/// print two SIMD vector of 4 doubles
LOCAL void dump(vec4 v, vec4 w, char const* s, char end='\n')
{
    printf(STG_F "d( " FLT_F FLT_F FLT_F FLT_F " )( " FLT_F FLT_F FLT_F FLT_F " )%c",
           s, v[3], v[2], v[1], v[0], w[3], w[2], w[1], w[0], end);
}

/// print SIMD vector of 8 floats
LOCAL void dump(__m256 v, char const* s, char end='\n')
{
    printf(STG_F "f( " FLT_F FLT_F FLT_F FLT_F FLT_F FLT_F FLT_F FLT_F ")%c", s,
           v[7], v[6], v[5], v[4], v[3], v[2], v[1], v[0], end);
}

#endif

#undef LOCAL

#endif
