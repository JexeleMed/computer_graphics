#!/usr/bin/env python3
# Zadanie 4 (ocena 4.5): prostokątny dywan Sierpińskiego rysowany rekurencyjnie.
# Użycie: uv run lab2/zad4_sierpinski_carpet.py [level]   (level = stopień samopodobieństwa, domyślnie 3)

import sys  # sys.exit() przy błędach krytycznych oraz sys.argv dla parametru poziomu z wiersza poleceń.

from glfw.GLFW import *  # GLFW: tworzy okno i kontekst OpenGL oraz obsługuje zdarzenia wejścia (nazwy w stylu C).

from OpenGL.GL import *  # Podstawowe funkcje OpenGL (gl*) i stałe (GL_*).
from OpenGL.GLU import *  # Biblioteka pomocnicza OpenGL (glu*); jeszcze nieużywana, zostaje dla zgodności z szablonem z zajęć.

LEVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 4  # Głębokość rekurencji z 1. argumentu wiersza poleceń, 4 jeśli nie podano.

CARPET_WIDTH = 180.0  # Szerokość całego dywanu w jednostkach świata (widok obejmuje ok. 200).
CARPET_HEIGHT = 120.0  # Wysokość całego dywanu; inna niż szerokość -> dywan "prostokątny".


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


def draw_carpet(x, y, a, b, level):  # Dywan o środku w (x, y), rozmiarze a x b, z pozostałymi "level" krokami podziału.
    if level <= 0:  # Przypadek bazowy: koniec podziału...
        draw_rectangle(x, y, a, b)  # ...więc po prostu rysujemy pełny prostokąt.
        return  # I kończymy w tym miejscu rekurencję.

    third_a = a / 3.0  # Szerokość jednej komórki siatki 3x3.
    third_b = b / 3.0  # Wysokość jednej komórki siatki 3x3.

    for i in (-1, 0, 1):  # Kolumna siatki 3x3: lewa, środkowa, prawa.
        for j in (-1, 0, 1):  # Wiersz siatki 3x3: dolny, środkowy, górny.
            if i == 0 and j == 0:  # Środkowa komórka...
                continue  # ...jest dziurą: pomiń ją (widoczny pozostaje kolor tła).
            draw_carpet(x + i * third_a,  # Środek X tej komórki: przesunięty o szerokość komórki w lewo/prawo.
                        y + j * third_b,  # Środek Y tej komórki: przesunięty o wysokość komórki w dół/górę.
                        third_a, third_b,  # Każda komórka jest 3x mniejsza w obu kierunkach.
                        level - 1)  # O jeden poziom mniej -> rekurencja w końcu dojdzie do przypadku bazowego.


def render(time):  # Rysuje jedną klatkę; "time" = sekundy od glfwInit() (tu nieużywane).
    glClear(GL_COLOR_BUFFER_BIT)  # Wypełnij cały bufor koloru białym kolorem czyszczenia.

    glColor3f(0.6, 0.2, 0.0)  # Ceglasty brąz, jak na slajdzie z instrukcją; używany przez każdy prostokąt poniżej.
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
