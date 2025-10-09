// Cytosim was created by Francois Nedelec. Copyright 2022 Cambridge University

#include <cstdio>

// include the OpenGL header depending on platform
#if 0
#   include "gles2.h"
#elif defined(__APPLE__)
#   include <OpenGL/gl.h>
#elif ( 1 )
#   include <GL/glew.h>
#else
#   define GLAD_GL_IMPLEMENTATION
#   include <glad/gl.h>
#endif

/// must be called to initialize OpenGL
void initializeOpenGL();

/// print info about OpenGL
void documentOpenGL(FILE*);

/// convert OpenGL error code to string
const char* glErrorString(unsigned code);

/// check and print OpenGL error(s)
void reportOpenGLErrors(FILE*, const char* msg);

/// powerful debug function available with OpenGL 4.3
void enableOpenGLdebug();

/// These values should be defined in OpenGL/glext.h

#ifndef GL_MULTISAMPLE
#  define GL_MULTISAMPLE 0x809D
#endif

#ifndef GL_DEPTH_CLAMP
#  define GL_DEPTH_CLAMP 0x864F
#endif
