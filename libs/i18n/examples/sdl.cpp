#include <iostream>
#include <SDL.h>
#include <windows.h>

// You shouldn't really use this statement, but it's fine for small programs
using namespace std;

// You must include the command line parameters for your main function to be recognized by SDL
int CALLBACK WinMain(HINSTANCE h, HINSTANCE _p, LPSTR l, int n) {

	SDL_Window* window = NULL;
    SDL_Renderer* renderer = NULL;

    // Initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        // Handle error
        return 1;
    }

    // Create a window
    window = SDL_CreateWindow("My SDL Window", 100, 100, 800, 600, SDL_WINDOW_SHOWN);
    if (window == NULL) {
        // Handle error
        SDL_Quit();
        return 1;
    }

    // Create a renderer
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer == NULL) {
        // Handle error
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Set background color to blue
    SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255);

    // Clear the renderer
    SDL_RenderClear(renderer);

    // Present the renderer
    SDL_RenderPresent(renderer);

    // Wait for a few seconds
    SDL_Delay(10000);

    // Clean up
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}