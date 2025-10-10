// Cytosim was created by Francois Nedelec. Copyright 2025 Cambridge University

#include <iostream>
#include <sstream>

/** This scales the 3D points by (X, Y, Z) */
template < typename FLOAT >
static void scaleVertices(size_t num, FLOAT* ptr, FLOAT X, FLOAT Y, FLOAT Z)
{
    for ( FLOAT * end = ptr + 3 * num; ptr < end; ptr += 3 )
    {
        ptr[0] *= X;
        ptr[1] *= Y;
        ptr[2] *= Z;
    }
}


/** This scales the 3D points by (X, Y, Z) */
template < typename FLOAT >
static void translateVertices(size_t num, FLOAT* ptr, FLOAT X, FLOAT Y, FLOAT Z)
{
    for ( FLOAT * end = ptr + 3 * num; ptr < end; ptr += 3 )
    {
        ptr[0] += X;
        ptr[1] += Y;
        ptr[2] += Z;
    }
}


/** print min-max of (X, Y, Z) coordinates */
template < typename FLOAT >
static void infoVertices(const char msg[], size_t num, FLOAT* ptr)
{
    FLOAT iX = INFINITY, sX = -INFINITY;
    FLOAT iY = INFINITY, sY = -INFINITY;
    FLOAT iZ = INFINITY, sZ = -INFINITY;
    for ( FLOAT * end = ptr + 3 * num; ptr < end; ptr += 3 )
    {
        iX = std::min(iX, ptr[0]);
        sX = std::max(sX, ptr[0]);
        iY = std::min(iY, ptr[1]);
        sY = std::max(sY, ptr[1]);
        iZ = std::min(iZ, ptr[2]);
        sZ = std::max(sZ, ptr[2]);
    }
    std::clog << msg << " X in [ " << iX << "  " << sX << " ]\n";
    std::clog << msg << " Y in [ " << iY << "  " << sY << " ]\n";
    std::clog << msg << " Z in [ " << iZ << "  " << sZ << " ]\n";
}
