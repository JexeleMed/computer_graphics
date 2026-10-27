#!/usr/bin/env python3
# Zadanie 5 (ocena 5.0): znów dywan Sierpińskiego, ale ITERACYJNIE (bez rekurencji) - alternatywa dopuszczona przez slajdy.
# Idea ("dziedzina dozwolonych współrzędnych"): podziel dywan na siatkę komórek 3^n x 3^n. Komórka (i, j) jest dziurą,
# jeśli na jakiejś pozycji cyfry trójkowe ZARÓWNO i, jak i j wynoszą 1 (= środkowa trzecia część na tym poziomie podziału).
# Użycie: uv run lab2/zad5_sierpinski_iterative.py [level]   (domyślnie 3)

import sys  # sys.exit() przy błędach krytycznych oraz sys.argv dla parametru poziomu z wiersza poleceń.

from glfw.GLFW import *  # GLFW: tworzy okno i kontekst OpenGL oraz obsługuje zdarzenia wejścia (nazwy w stylu C).

from OpenGL.GL import *  # Podstawowe funkcje OpenGL (gl*) i stałe (GL_*).
from OpenGL.GLU import *  # Biblioteka pomocnicza OpenGL (glu*); jeszcze nieużywana, zostaje dla zgodności z szablonem z zajęć.

LEVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 4  # Stopień samopodobieństwa z 1. argumentu wiersza poleceń, 4 jeśli nie podano.

CARPET_WIDTH = 180.0  # Szerokość całego dywanu w jednostkach świata.
CARPET_HEIGHT = 120.0  # Wysokość całego dywanu.


def startup(window):  # Wykonywana raz, gdy kontekst OpenGL jest gotowy, przed główną pętlą.
    width, height = glfwGetFramebufferSize(window)  # Rozmiar w PIKSELACH (na Retinie jest 2x większy niż rozmiar okna w punktach).
    update_viewport(window, width, height)  # Ustaw viewport i projekcję dla początkowego rozmiaru.
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Białe tło: prześwituje przez dziury w dywanie.


def shutdown():  # Wykonywana raz po zakończeniu głównej pętli; miejsce na zwolnienie zasobów OpenGL.
    pass  # Nic do zwolnienia w tym programie.


def draw_rectangle(x, y, a, b):  # Prostokąt o środku w (x, y), szerokości a i wysokości b, zbudowany z dwóch trójkątów.
    half_a = a / 2.0  # Połowa szerokości.
    half_b = b / 2.0  # Połowa wysokości.

    glBegin(GL_TRIANGLES)  # 6 wierzchołków -> 2 trójkąty.
    glVertex2f(x - half_a, y - half_b)  # Trójkąt 1: lewy dolny.
    glVertex2f(x + half_a, y - half_b)  # Trójkąt 1: prawy dolny.
    glVertex2f(x - half_a, y + half_b)  # Trójkąt 1: lewy górny.
    glVertex2f(x + half_a, y - half_b)  # Trójkąt 2: prawy dolny.
    glVertex2f(x + half_a, y + half_b)  # Trójkąt 2: prawy górny.
    glVertex2f(x - half_a, y + half_b)  # Trójkąt 2: lewy górny.
    glEnd()  # Zakończ dwa trójkąty.


def is_filled(i, j):  # True, jeśli komórka siatki (kolumna i, wiersz j) należy do dywanu, False, jeśli leży w jakiejś dziurze.
    while i > 0 or j > 0:  # Sprawdzaj cyfry trójkowe od najmniej znaczącej, aż obie liczby się wyczerpią.
        if i % 3 == 1 and j % 3 == 1:  # Obie cyfry to 1 -> środkowa kolumna ORAZ środkowy wiersz na tym poziomie...
            return False  # ...więc komórka leży w wyciętej dziurze.
        i //= 3  # Odrzuć ostatnią cyfrę trójkową i (dzielenie całkowite)...
        j //= 3  # ...oraz j, przechodząc na następny (większy) poziom podziału.
    return True  # Żaden poziom nie umieścił tej komórki w dziurze -> należy do dywanu.


def draw_carpet(x, y, a, b, level):  # Dywan o środku w (x, y), rozmiarze a x b, "level" podziałów - bez rekurencji.
    cells = 3 ** level  # Liczba komórek wzdłuż każdego boku najdrobniejszej siatki (3^level).
    cell_a = a / cells  # Szerokość pojedynczej komórki.
    cell_b = b / cells  # Wysokość pojedynczej komórki.
    left = x - a / 2.0  # X lewej krawędzi dywanu.
    bottom = y - b / 2.0  # Y dolnej krawędzi dywanu.

    for i in range(cells):  # Każda kolumna siatki...
        for j in range(cells):  # ...i każdy wiersz: zwykłe zagnieżdżone pętle zamiast rekurencji.
            if is_filled(i, j):  # Rysuj tylko komórki należące do dywanu.
                draw_rectangle(left + (i + 0.5) * cell_a,  # Środek X komórki i: lewa krawędź + i i pół komórki.
                               bottom + (j + 0.5) * cell_b,  # Środek Y komórki j: dolna krawędź + j i pół komórki.
                               cell_a, cell_b)  # Rozmiar jednej komórki.


def render(time):  # Rysuje jedną klatkę; "time" = sekundy od glfwInit() (tu nieużywane).
    glClear(GL_COLOR_BUFFER_BIT)  # Wypełnij cały bufor koloru białym kolorem czyszczenia.

    glColor3f(0.0, 0.35, 0.6)  # Ciemnoniebieski, aby od razu odróżnić od wersji rekurencyjnej.
    draw_carpet(0.0, 0.0, CARPET_WIDTH, CARPET_HEIGHT, LEVEL)  # Cały dywan wyśrodkowany w oknie.

    glFlush()  # Wypchnij wszystkie zakolejkowane polecenia OpenGL do GPU w celu wykonania.


def update_viewport(window, width, height):  # Wywoływana na starcie i przy każdej zmianie rozmiaru framebuffera.
    if height == 0:  # Zminimalizowane okno może zgłosić wysokość 0...
        height = 1  # ...co spowodowałoby dzielenie przez zero poniżej, więc ograniczamy ją.
    if width == 0:  # To samo zabezpieczenie dla szerokości...
        width = 1  # ...aby proporcje obrazu zawsze były poprawną liczbą dodatnią.
    aspect_ratio = width / height  # Stosunek szerokości do wysokości, używany, by kształty nie były rozciągane.

    glMatrixMode(GL_PROJECTION)  # Kolejne wywołania macierzowe modyfikują macierz PROJEKCJI (odwzorowanie świat -> ekran).
    glViewport(0, 0, width, height)  # Odwzoruj wyjście OpenGL na cały framebuffer: x, y lewego dolnego rogu, szerokość, wysokość.
    glLoadIdentity()  # Zresetuj macierz projekcji do jednostkowej (porzuć poprzednią projekcję).

    if width <= height:  # Okno jest wysokie (lub kwadratowe): X zachowuje zakres [-100, 100]...
        glOrtho(-100.0, 100.0, -100.0 / aspect_ratio, 100.0 / aspect_ratio,  # ...a zakres Y jest rozciągnięty.
                1.0, -1.0)  # Bliska/daleka płaszczyzna obcinania wzdłuż Z; w 2D między nimi musi zmieścić się tylko z = 0.
    else:  # Okno jest szerokie: Y zachowuje zakres [-100, 100]...
        glOrtho(-100.0 * aspect_ratio, 100.0 * aspect_ratio, -100.0, 100.0,  # ...a zakres X jest rozciągnięty.
                1.0, -1.0)  # Te same płaszczyzny obcinania co wyżej.

    glMatrixMode(GL_MODELVIEW)  # Wróć do macierzy MODELVIEW (transformacje obiektów) używanej podczas rysowania.
    glLoadIdentity()  # Zacznij bez transformacji: współrzędne wierzchołków są użyte takie, jakie podano.


def main():  # Punkt wejścia programu: konfiguracja okna i główna pętla.
    if not glfwInit():  # Zainicjuj bibliotekę GLFW; przy niepowodzeniu zwraca false.
        sys.exit(-1)  # Bez GLFW nie otworzymy okna, więc zakończ z kodem błędu.

    window = glfwCreateWindow(600, 400, __file__, None, None)  # Okno 600x400 (szerokie, by pasował szeroki dywan).
    if not window:  # Nie udało się utworzyć okna (lub jego kontekstu OpenGL)...
        glfwTerminate()  # ...zwolnij to, co zaalokowało glfwInit()...
        sys.exit(-1)  # ...i zakończ z kodem błędu.

    glfwMakeContextCurrent(window)  # Ustaw kontekst OpenGL tego okna jako bieżący: wszystkie wywołania gl* dotyczą teraz jego.
    glfwSetFramebufferSizeCallback(window, update_viewport)  # Wywołuj update_viewport(window, w, h) przy każdej zmianie rozmiaru okna.
    glfwSwapInterval(1)  # Włącz V-Sync: zamieniaj bufory co najwyżej raz na odświeżenie monitora.

    startup(window)  # Jednorazowa inicjalizacja naszego stanu OpenGL.
    while not glfwWindowShouldClose(window):  # Pętla trwa, dopóki użytkownik nie zamknie okna.
        render(glfwGetTime())  # Narysuj nową klatkę w ukrytym (tylnym) buforze.
        glfwSwapBuffers(window)  # Pokaż tylny bufor na ekranie i zamień go z przednim (podwójne buforowanie).
        glfwWaitEvents()  # Śpij do nadejścia zdarzenia (zmiana rozmiaru, klawisz, mysz...), następnie je obsłuż.
    shutdown()  # Jednorazowe sprzątanie po pętli.

    glfwTerminate()  # Zniszcz okno i zwolnij wszystkie zasoby GLFW.


if __name__ == '__main__':  # Prawda tylko gdy plik jest uruchamiany bezpośrednio, a nie importowany jako moduł.
    main()  # Uruchom program.
