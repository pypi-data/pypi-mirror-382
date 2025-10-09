// Cytosim was created by Francois Nedelec. Copyright 2021 Cambridge University.

#include "gle.h"
#include "gym_color.h"
#include "glut.h"
#include "glapp.h"
#include "gym_cap.h"
#include "gym_check.h"
#include "gym_flute.h"
#include "gym_draw.h"
#include "gym_view.h"
#include "fg_stroke.h"
#include "tesselator.h"
#include <cstdio>

int kind = 2;
int rank = 1;

int showPlane = 0;
int showNames = 0;
int showPoints = 0;
int showEdges = 2;
int showFaces = 1;

Tesselator * ico = nullptr;

GLint cull_test = true;

GLuint buffers[4] = { 0 };

void flip_cap(GLenum cap)
{
    GLint i = glIsEnabled(cap);
    if ( i )
        glDisable(cap);
    else
        glEnable(cap);
    gym::printCaps("flip");
}

//------------------------------------------------------------------------------
void initVBO();

void reset(int K, int R)
{
    kind = abs(K);
    rank = R;
    if ( ico )
        delete ico;
    ico = new Tesselator();
    ico->construct((Tesselator::Polyhedra)K, R, 7);

    char tmp[128];
    snprintf(tmp, sizeof(tmp), "%i div, %i points, %i faces, %i edges",
             R, ico->numVertices(), ico->numFaces(), ico->numEdges());
    glApp::setMessage(tmp);
    initVBO();
}

FILE * openFile(const char name[])
{
    FILE * f = fopen(name, "w");

    if ( !f || ferror(f) )
    {
        glApp::flashText("input file could not be opened");
        return nullptr;
    }
    if ( ferror(f) )
    {
        fclose(f);
        glApp::flashText("input file opened with error");
        return nullptr;
    }
    return f;
}

void exportPLY()
{
    FILE * f = openFile("mesh.ply");
    if ( f ) {
        ico->exportPLY(f);
        fclose(f);
        glApp::flashText("exported `mesh.ply'");
    }
}

void exportSTL()
{
    FILE * f = openFile("mesh.stl");
    if ( f ) {
        ico->exportSTL(f);
        fclose(f);
        glApp::flashText("exported `mesh.stl'");
    }
}

//------------------------------------------------------------------------------

void drawPlane()
{
    flute3 * flu = gym::mapBufferV3(4);
    flu[0] = { 1, 1, 0};
    flu[1] = {-1, 1, 0};
    flu[2] = { 1,-1, 0};
    flu[3] = {-1,-1, 0};
    gym::unmapBufferV3();
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
}


void drawFacesArray()
{
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_NORMAL_ARRAY);
    
    flute3 * flu = gym::mapBufferV3(4);
    ico->storeVertices((float*)flu);
    gym::unmapBufferV3N0();
    glDrawElements(GL_TRIANGLES, 3*ico->numFaces(), GL_UNSIGNED_SHORT, ico->faceData());
    glDisableClientState(GL_NORMAL_ARRAY);
    //glDisableClientState(GL_VERTEX_ARRAY);
}


void initVBO()
{
    glGenBuffers(4, buffers);
    
    // calculate vertex data directly into device memory
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0]);
    glBufferData(GL_ARRAY_BUFFER, 3*ico->numVertices()*sizeof(float), nullptr, GL_STATIC_DRAW);
    void * glb = glMapBuffer(GL_ARRAY_BUFFER, GL_WRITE_ONLY);
    ico->storeVertices((float*)glb);
    glUnmapBuffer(GL_ARRAY_BUFFER);
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    
    // create a new VBO for vertex indices defining the triangles
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[1]);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 3*ico->numFaces()*sizeof(Tesselator::INDEX), ico->faceData(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
    
    // create a new VBO for vertex indices defining the edges
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2]);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 2*ico->numEdges()*sizeof(Tesselator::INDEX), ico->edgeData(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
}


void drawFacesVBO()
{
    glEnableClientState(GL_NORMAL_ARRAY);
    glEnableClientState(GL_VERTEX_ARRAY);

    glBindBuffer(GL_ARRAY_BUFFER, buffers[0]);
    glVertexPointer(3, GL_FLOAT, 0, nullptr);
    glNormalPointer(GL_FLOAT, 0, nullptr);
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[1]);
    static_assert(std::is_same<Tesselator::INDEX, GLushort>::value, "Index type mismatch");
    glDrawElements(GL_TRIANGLES, 3*ico->numFaces(), GL_UNSIGNED_SHORT, nullptr);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
    
    glDisableClientState(GL_NORMAL_ARRAY);
    //glDisableClientState(GL_VERTEX_ARRAY);
}


void drawEdges()
{
#if 0
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    drawFacesArray();
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
#else
    if ( showEdges == 2 )
    {
        flute3 * flu = gym::mapBufferV3(ico->numVertices());
        ico->storeVertices((float*)flu);
        gym::unmapBufferV3();
    }
    else
    {
        glBindBuffer(GL_ARRAY_BUFFER, buffers[0]);
        glVertexPointer(3, GL_FLOAT, 0, nullptr);
    }
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2]);
    glLineWidth(0.5);
    glDrawElements(GL_LINES, 2 * ico->numEdges(), GL_UNSIGNED_SHORT, nullptr);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
#endif
}

void namePoints(View& view)
{
    const float S = 1.03;
    gym::disableLighting();
    gym::disableAlphaTest();
    gym::cancelRotation();
    char tmp[128];
    for ( unsigned i=0; i < ico->numVertices(); ++i )
    {
        float scale = 1.f;
        Tesselator::Vertex & dv = ico->vertex(i);
        float col[4] = {1.f, 0.f, 0.f, 1.f};
        if ( dv.weight(2) == 0 )
        { col[1] = 1; scale = 1.4142f; }
        if ( dv.weight(1) == 0 )
        { col[2] = 1; scale = 2.f; }
        
        gym::color(col);
        const float* ptr = ico->vertexData(i);
        snprintf(tmp, sizeof(tmp), "%u", i);
        view.strokeString(S*ptr[0], S*ptr[1], S*ptr[2], tmp, scale);
    }
    gym::restoreAlphaTest();
    gym::restoreLighting();
    gym::load_ref();
}

void drawPoints()
{
    glColor3f(1, 1, 1);
    if ( showPoints == 2 )
    {
        glBindBuffer(GL_ARRAY_BUFFER, buffers[0]);
        glVertexPointer(3, GL_FLOAT, 0, nullptr);
        glBindBuffer(GL_ARRAY_BUFFER, 0);
    }
    else
    {
        flute3 * flu = gym::mapBufferV3(ico->numVertices());
        ico->storeVertices((float*)flu);
        gym::unmapBufferV3();
   }
    gym::drawPoints(10, 0, ico->numVertices());
}

void drawSkeleton()
{
    glLineWidth(1);
    glPointSize(10);
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    glColor4f(0, 1, 1, 0.5f);
    glEnable(GL_LIGHTING);
    //gle::sphere1();
    //gle::needle();
    gle::football();
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
    glDisable(GL_LIGHTING);
}

int display(View& view)
{
    view.openDisplay();
    glShadeModel(GL_FLAT);
    GLfloat blue[4] = { 0, 0, 1, 1 };
    GLfloat pink[4] = { 1.0, 0.0, 0.7, 1 };
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, blue);
    glMaterialfv(GL_BACK, GL_AMBIENT_AND_DIFFUSE, pink);

    //drawSkeleton();
    glDepthMask(GL_TRUE);
    if ( showPlane )
    {
        glDisable(GL_LIGHTING);
        drawPlane();
    }
    if ( showFaces )
    {
        glEnable(GL_LIGHTING);
        if ( cull_test )
            glEnable(GL_CULL_FACE);
        glCullFace(GL_BACK);
        if ( showFaces == 2 )
            drawFacesArray();
        else
            drawFacesVBO();
        glDisable(GL_CULL_FACE);
    }
    if ( showEdges )
    {
        glDisable(GL_LIGHTING);
        glColor3f(1, 1, 1);
        drawEdges();
    }
    if ( showPoints )
    {
        glDisable(GL_LIGHTING);
        drawPoints();
    }
    if ( showNames )
    {
        glDisable(GL_LIGHTING);
        gym::color(1, 1, 1);
        namePoints(view);
    }
    view.closeDisplay();
    return 0;
}

//------------------------------------------------------------------------------

void processNormalKey(unsigned char c, int x, int y)
{
    switch (c)
    {
        case ' ': reset(kind, rank); break;
        case 'i': reset(Tesselator::ICOSAHEDRON, rank); break;
        case 'I': reset(Tesselator::IKOSAHEDRON, rank); break;
        case 'o': reset(Tesselator::OCTAHEDRON, rank); break;
        case 'd': reset(Tesselator::DICE, rank); break;
        case 'h': reset(Tesselator::HEMISPHERE, rank); break;
        case 'a': reset(Tesselator::DROPLET, rank); break;
        case 'A': reset(Tesselator::PIN, rank); break;
        case 'c': reset(Tesselator::CYLINDER, rank); break;
        case 't': reset(Tesselator::TETRAHEDRON, rank); break;
        case ']': reset(kind, rank+1); break;
        case '}': reset(kind, rank+16); break;
        case '[': reset(kind, std::max(rank-1, 1)); break;
        case '{': reset(kind, std::max(rank-16, 1)); break;
        
        case 'y': exportPLY(); return;
        case 'Y': exportSTL(); return;
            
        case 'e': showEdges = !showEdges; break;
        case 'E': showEdges = 2 * !showEdges; break;
        case 'f': showFaces = !showFaces; break;
        case 'F': showFaces = 2 * !showFaces; break;
        case 'n': showNames = !showNames; break;
        case 'p': showPoints = !showPoints; break;
        case 'P': showPoints = 2 * !showPoints; break;
        case 'v': showPlane = !showPlane; break;
        case 'C': cull_test = !cull_test; break;
        case 'D': flip_cap(GL_DEPTH_TEST); break;

        default: glApp::processNormalKey(c,x,y); return;
    }
    glApp::postRedisplay();
}

//------------------------------------------------------------------------------

int main(int argc, char* argv[])
{
    initializeOpenGL();
    glutInit(&argc, argv);
    glApp::setDimensionality(3);
    glApp::normalKeyFunc(processNormalKey);
    glApp::newWindow(display);
    glApp::attachMenu();
    glApp::setScale(3);
    gle::initialize();
    reset(kind, rank);
    glutMainLoop();
}
