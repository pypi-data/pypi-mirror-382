// Cytosim was created by Francois Nedelec. Copyright 2025 Cambridge University

#include "opengl.h"
#include <stdlib.h>

void initializeOpenGL()
{
#ifdef __GLEXT_H_
    //need to initialize GLEW on Linux
    const GLenum err = glewInit();
    if ( GLEW_OK != err )
    {
        /* Problem: glewInit failed, something is seriously wrong. */
        fprintf(stderr, "Error: %s\n", glewGetErrorString(err));
        exit(1);
    }
#warning "initializeOpenGL() will initialize GLEW"
    //documentOpenGL(stdout);
#endif
    //enableOpenGLdebug();
}


/** This will work only if OpenGL was correctly initialized */
void documentOpenGL(FILE * out)
{
    GLubyte const* str = glGetString(GL_VENDOR);
    fprintf(out, "GL_VENDOR   %s\n", str);
    str = glGetString(GL_VERSION);
    fprintf(out, "GL_VERSION  %s\n", str);
    str = glGetString(GL_RENDERER);
    fprintf(out, "GL_RENDERER %s\n", str);
}


char const* glErrorString(unsigned code)
{
    switch ( code )
    {
        case GL_NO_ERROR:          return "GL_NO_ERROR";
        case GL_INVALID_ENUM:      return "GL_INVALID_ENUM";
        case GL_INVALID_VALUE:     return "GL_INVALID_VALUE";
        case GL_INVALID_OPERATION: return "GL_INVALID_OPERATION";
        case GL_STACK_OVERFLOW:    return "GL_STACK_OVERFLOW";
        case GL_STACK_UNDERFLOW:   return "GL_STACK_UNDERFLOW";
        case GL_OUT_OF_MEMORY:     return "GL_OUT_OF_MEMORY";
        case GL_TABLE_TOO_LARGE:   return "GL_TABLE_TOO_LARGE";
        default:                   return "GL_UNKNOWN_ERROR";
    }
}

/**
 This check for OpenGL errors,
 the argument 'msg' can be useful to provide feedback for debugging
 */
void reportOpenGLErrors(FILE * out, const char* msg)
{
    GLenum e = glGetError();
    while ( e != GL_NO_ERROR )
    {
        fprintf(out, "OpenGL error `%s' %s\n", glErrorString(e), msg);
        e = glGetError();
    }
}

//--------------------------------------------------------------------------

/// These values should be defined in OpenGL/gl3.h

#ifndef GL_DEBUG_OUTPUT
#  define GL_DEBUG_OUTPUT 0x92E0
#endif

#ifndef GL_DEBUG_OUTPUT_SYNCHRONOUS
#  define GL_DEBUG_OUTPUT_SYNCHRONOUS 0x8242
#endif


#ifdef GL_VERSION_4_3

void glErrorCallback(GLenum source, GLenum type, GLuint id,
                     GLenum severity, GLsizei length,
                     const GLchar* message, const void* userParam)
{
    fprintf(stderr, "OpenGL Message: %s\n", message);
}

void enableOpenGLdebug()
{
    glEnable(GL_DEBUG_OUTPUT);
    glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS);
    glDebugMessageCallback(glErrorCallback, nullptr);
}

#endif
