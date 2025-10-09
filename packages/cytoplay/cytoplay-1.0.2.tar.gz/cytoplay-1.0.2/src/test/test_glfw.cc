#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cassert>

float zoom = 0.8f;
float focus[2] = {0.0f, 0.0f};
int winW = 800, winH = 800;

int buttonStatus = 0;
double timerDelay = 0.1;
float pointer[2] = {0.0f, 0.0f};
int pointSize = 7;

// Simple vertex and fragment shaders
const char* vertexShaderSrc = R"(
#version 330 core
layout(location = 0) in vec2 aPos;
uniform mat4 uMVP;
uniform float uPSize;
void main() {
    gl_Position = uMVP * vec4(aPos, 0.0, 1.0);
    gl_PointSize = uPSize;
}
)";

const char* fragmentShaderSrc = R"(
#version 330 core
out vec4 FragColor;
uniform vec4 uColor;
uniform float uPSize;
void main() {
    if ( uPSize > 0 )
    {
        vec2 v = gl_PointCoord - 0.5f;
        if (dot(v,v) >= 0.25f) discard;
    }
    FragColor = uColor;
}
)";

void compileShader(GLuint shader)
{
    glCompileShader(shader);
    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char log[1024];
        glGetShaderInfoLog(shader, sizeof(log), NULL, log);
        printf("Shader compilation failed:\n%s\n", log);
    }
}

GLuint createShaderProgram(const char* vsSrc, const char* fsSrc)
{
    GLuint vs = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vs, 1, &vsSrc, nullptr);
    compileShader(vs);
    
    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &fsSrc, nullptr);
    compileShader(fs);
    
    GLuint program = glCreateProgram();
    glAttachShader(program, vs);
    glAttachShader(program, fs);
    glLinkProgram(program);

    glDeleteShader(vs);
    glDeleteShader(fs);
    return program;
}

float triangleVertices[] = {
    1.0f, -1.0f,
   -1.0f, -1.0f,
    0.0f,  1.0f
};

GLuint triangleVAO, triangleVBO;
GLuint pointVAO, pointVBO;

GLuint shaderProgram;
GLint uMVP, uColor, uPSize;

void createVAOs()
{
    glGenVertexArrays(1, &triangleVAO);
    glGenBuffers(1, &triangleVBO);

    glBindVertexArray(triangleVAO);
    glBindBuffer(GL_ARRAY_BUFFER, triangleVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(triangleVertices), triangleVertices, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glEnable(GL_PROGRAM_POINT_SIZE);

    // Point VAO (1 point, dynamically updated)
    glGenVertexArrays(1, &pointVAO);
    glGenBuffers(1, &pointVBO);
    glBindVertexArray(pointVAO);
    glBindBuffer(GL_ARRAY_BUFFER, pointVBO);
    glBufferData(GL_ARRAY_BUFFER, 2 * sizeof(float), pointer, GL_DYNAMIC_DRAW);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
}

void updatePointerBuffer()
{
    glBindBuffer(GL_ARRAY_BUFFER, pointVBO);
    glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(pointer), pointer);
}

void calculateOrthoProjection(float* mvp)
{
    float aspect = (float)winW / winH;
    float zoomedW = 2.0f / zoom;
    float zoomedH = zoomedW / aspect;

    float L = focus[0] - zoomedW / 2.0f;
    float R = focus[0] + zoomedW / 2.0f;
    float B = focus[1] - zoomedH / 2.0f;
    float T = focus[1] + zoomedH / 2.0f;

    mvp[0] = 2.0f / (R - L); mvp[4] = 0.0f;           mvp[8] = 0.0f;  mvp[12] = -(R + L) / (R - L);
    mvp[1] = 0.0f;           mvp[5] = 2.0f / (T - B); mvp[9] = 0.0f;  mvp[13] = -(T + B) / (T - B);
    mvp[2] = 0.0f;           mvp[6] = 0.0f;           mvp[10] = -1.0f; mvp[14] = 0.0f;
    mvp[3] = 0.0f;           mvp[7] = 0.0f;           mvp[11] = 0.0f;  mvp[15] = 1.0f;
}

void renderScene()
{
    glClear(GL_COLOR_BUFFER_BIT);
    float mvp[16];
    calculateOrthoProjection(mvp);
    glUseProgram(shaderProgram);
    glUniformMatrix4fv(uMVP, 1, GL_FALSE, mvp);

    // Draw triangle
    glUniform1f(uPSize, 0.f);
    glUniform4f(uColor, 1.f, 1.f, 1.f, 1.f);
    glBindVertexArray(triangleVAO);
    glDrawArrays(GL_LINE_LOOP, 0, 3);

    // Draw pointer
    updatePointerBuffer();
    glUniform1f(uPSize, (float)pointSize);
    glUniform4f(uColor, 1.f, 1.f, 0.f, 1.f);
    glBindVertexArray(pointVAO);
    glDrawArrays(GL_POINTS, 0, 1);
}

void framebuffer_size_callback(GLFWwindow*, int w, int h)
{
    winW = w;
    winH = h;
    glViewport(0, 0, w, h);
}

void mouse_button_callback(GLFWwindow*, int button, int action, int mods)
{
    if (button == GLFW_MOUSE_BUTTON_LEFT)
    {
        buttonStatus = action;
        if ( action == GLFW_PRESS ) {
            double x, y;
            glfwGetCursorPos(glfwGetCurrentContext(), &x, &y);
            pointer[0] = ((x / winW) - 0.5f) * (2.0f / zoom) + focus[0];
            pointer[1] = ((0.5f - y / winH)) * (2.0f / zoom) + focus[1];
        }
    }
}

void mouse_motion_callback(GLFWwindow*, double x, double y)
{
    if ( buttonStatus == GLFW_PRESS )
    {
        pointer[0] = ((x / winW) - 0.5f) * (2.0f / zoom) + focus[0];
        pointer[1] = ((0.5f - y / winH)) * (2.0f / zoom) + focus[1];
    }
}

void key_callback(GLFWwindow* window, int key, int, int action, int)
{
    if (action != GLFW_PRESS) return;
    if (key == GLFW_KEY_ESCAPE || key == GLFW_KEY_Q)
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else if (key == GLFW_KEY_SPACE)
        zoom = 1.0f;
}

int main()
{
    if (!glfwInit()) return EXIT_FAILURE;
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    GLFWwindow* win = glfwCreateWindow(winW, winH, "GL ES2-like with Shaders", nullptr, nullptr);
    if (!win) { glfwTerminate(); return EXIT_FAILURE; }
    glfwMakeContextCurrent(win);
    gladLoadGL();
    //gladLoadGLES2Loader((GLADloadproc)glfwGetProcAddress);
    
    glfwSetFramebufferSizeCallback(win, framebuffer_size_callback);
    glfwSetMouseButtonCallback(win, mouse_button_callback);
    glfwSetCursorPosCallback(win, mouse_motion_callback);
    glfwSetKeyCallback(win, key_callback);

    shaderProgram = createShaderProgram(vertexShaderSrc, fragmentShaderSrc);
    uMVP = glGetUniformLocation(shaderProgram, "uMVP");
    uColor = glGetUniformLocation(shaderProgram, "uColor");
    uPSize = glGetUniformLocation(shaderProgram, "uPSize");
    assert(uMVP >= 0);
    assert(uColor >= 0);
    assert(uPSize >= 0);

    createVAOs();

    glClearColor(0.f, 0.f, 0.f, 1.f);

    double next = glfwGetTime() + timerDelay;
    while (!glfwWindowShouldClose(win))
    {
        if ( glfwGetTime() > next )
        {
            pointSize = 1 + (pointSize + 1) % 16;
            next = glfwGetTime() + timerDelay;
        }
        renderScene();
        glfwSwapBuffers(win);
        glfwPollEvents();
    }

    glfwDestroyWindow(win);
    glfwTerminate();
    return EXIT_SUCCESS;
}
