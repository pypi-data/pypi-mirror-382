
#include <cstdlib>
#include <cstdio>
#include <cmath>

#include "glfw.h"

int winW = 800, winH = 800;
float zoom = 0.8f;
float pixelSize = 1;
float focus[2] = {0.f, 0.f};
float pointer[3] = {0.f, 0.f, 0.f};
float mouseDown[3] = {0.f, 0.f, 0.f};
int pointSize = 1;

enum { MOUSE_PASSIVE, MOUSE_ZOOM, MOUSE_MOVE, MOUSE_CLICK };
int mouseAction = MOUSE_PASSIVE;
float zoomSave = 1.f, zoomFactor = 1.f;
double lastTime = 0;
int timerDelay = 50;

GLFWwindow* window;

void setModelView() {
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    glScalef(zoom, zoom, zoom);
    glTranslatef(-focus[0], -focus[1], 0);
}

void unproject(double x, double y, float res[2]) {
    res[0] = (x - 0.5f * winW) * pixelSize + focus[0];
    res[1] = (0.5f * winH - y) * pixelSize + focus[1];
}

void framebuffer_size_callback(GLFWwindow*, int w, int h) {
    winW = w;
    winH = h;
    glViewport(0, 0, w, h);
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    
    if (w > h) {
        pixelSize = 2.0f / (zoom * winW);
        float ratio = float(h) / float(w);
        glOrtho(-1.0, 1.0, -ratio, ratio, 0, 1);
    } else {
        pixelSize = 2.0f / (zoom * winH);
        float ratio = float(w) / float(h);
        glOrtho(-ratio, ratio, -1.0, 1.0, 0, 1);
    }
}

void key_callback(GLFWwindow*, int key, int, int action, int mods) {
    if (action != GLFW_PRESS) return;

    if (key == GLFW_KEY_ESCAPE || key == GLFW_KEY_Q)
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else if (key == GLFW_KEY_SPACE)
        zoom = 1.0f;

    setModelView();
}

void mouse_button_callback(GLFWwindow*, int button, int action, int mods) {
    if (action != GLFW_PRESS) return;

    double x, y;
    glfwGetCursorPos(window, &x, &y);

    mouseAction = MOUSE_PASSIVE;
    if (button == GLFW_MOUSE_BUTTON_LEFT) {
        mouseAction = (mods & GLFW_MOD_SHIFT) ? MOUSE_CLICK : MOUSE_MOVE;
    } else if (button == GLFW_MOUSE_BUTTON_MIDDLE) {
        mouseAction = MOUSE_ZOOM;
    }

    switch (mouseAction) {
        case MOUSE_MOVE: unproject(x, y, mouseDown); break;
        case MOUSE_ZOOM: {
            float xx = x - 0.5f * winW;
            float yy = y - 0.5f * winH;
            zoomFactor = sqrtf(xx * xx + yy * yy);
            if (zoomFactor > 0)
                zoomFactor = 1 / zoomFactor;
            zoomSave = zoom;
        } break;
        case MOUSE_CLICK: unproject(x, y, pointer); break;
        default: break;
    }
}

void cursor_position_callback(GLFWwindow*, double x, double y) {
    switch (mouseAction) {
        case MOUSE_MOVE: {
            float up[2];
            unproject(x, y, up);
            focus[0] += mouseDown[0] - up[0];
            focus[1] += mouseDown[1] - up[1];
        } break;
        case MOUSE_ZOOM: {
            float X = x - 0.5f * winW;
            float Y = y - 0.5f * winH;
            float Z = zoomFactor * sqrtf(X * X + Y * Y);
            if (Z > 0)
                zoom = zoomSave * Z;
        } break;
        case MOUSE_CLICK: unproject(x, y, pointer); break;
        default: break;
    }
    setModelView();
}

void initGL() {
    glClearColor(0.f, 0.f, 0.f, 0.f);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(GL_POINT_SMOOTH);
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST);
    glEnable(GL_LINE_SMOOTH);
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST);
    setModelView();
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    glColor3f(1.f, 1.f, 1.f);
    glLineWidth(1);

    glBegin(GL_LINE_LOOP);
    glVertex2f(1.f, -1.f);
    glVertex2f(-1.f, -1.f);
    glVertex2f(0.f, 1.f);
    glEnd();

    glColor3f(1.f, 1.f, 0.f);
    glPointSize(pointSize);
    glBegin(GL_POINTS);
    glVertex2f(pointer[0], pointer[1]);
    glEnd();

    glFinish();
}

void updateTimer() {
    double currentTime = glfwGetTime() * 1000.0;
    if (currentTime - lastTime >= timerDelay) {
        pointSize = 1 + (pointSize + 1) % 16;
        lastTime = currentTime;
    }
}

int main(int argc, char** argv) {
    if (!glfwInit()) {
        fprintf(stderr, "Failed to initialize GLFW\n");
        return EXIT_FAILURE;
    }

    window = glfwCreateWindow(winW, winH, "OpenGL GLFW", nullptr, nullptr);
    if (!window) {
        fprintf(stderr, "Failed to open GLFW window\n");
        glfwTerminate();
        return EXIT_FAILURE;
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
    glfwSetKeyCallback(window, key_callback);
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    glfwSetCursorPosCallback(window, cursor_position_callback);

    initGL();
    framebuffer_size_callback(window, winW, winH);
    glfwSetTime(0);
    lastTime = 0;

    while (!glfwWindowShouldClose(window)) {
        updateTimer();
        display();
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return EXIT_SUCCESS;
}
