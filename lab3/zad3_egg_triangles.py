#!/usr/bin/env python3
# Zadanie 3 (ocena 4.0): obracający się model jajka zbudowany z trójkątów (GL_TRIANGLES) z losowymi kolorami wierzchołków.
# Użycie: uv run lab3/zad3_egg_triangles.py [N]   (N = liczba próbek na parametr, domyślnie 20)

import sys  # sys.exit() przy błędach krytycznych oraz sys.argv dla parametru N z wiersza poleceń.
import random  # Liczby losowe dla kolorów wierzchołków.
from math import cos, sin, pi  # Trygonometria do równań parametrycznych; pi dla zakresu kątów.

from glfw.GLFW import *  # GLFW: tworzy okno i kontekst OpenGL oraz obsługuje zdarzenia wejścia (nazwy w stylu C).

from OpenGL.GL import *  # Podstawowe funkcje OpenGL (gl*) i stałe (GL_*).
from OpenGL.GLU import *  # Biblioteka pomocnicza OpenGL (glu*); jeszcze nieużywana, zostaje dla zgodności z szablonem z zajęć.

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20  # Liczba próbek u i v z 1. argumentu wiersza poleceń; N x N wierzchołków.

vertices = None  # Tablica N x N x 3 wierzchołków jajka; wypełniana raz w startup().
colors = None  # Tablica N x N x 3 kolorów RGB, po jednym na wierzchołek; wypełniana raz w startup().


def compute_egg(n):  # Próbkuje parametryczną powierzchnię jajka na siatce n x n wartości (u, v).
    tab = [[[0.0] * 3 for _ in range(n)] for _ in range(n)]  # Tablica n x n x 3; list comprehension zapobiega współdzieleniu podlist.
    for i in range(n):  # Indeks wiersza i <-> parametr u.
        u = i / (n - 1)  # Ostatnia wartość musi wynosić dokładnie 1.0, stąd n - 1.
        radius = -90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u  # Wspólny czynnik x i z.
        y = 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2 - 5  # Wysokość: -5 dla u = 0 i 1 (dół), 5 dla u = 0.5 (góra).
        for j in range(n):  # Indeks kolumny j <-> parametr v.
            v = j / (n - 1)  # v także biegnie od dokładnie 0.0 do dokładnie 1.0.
            tab[i][j][0] = radius * cos(pi * v)  # x: promień obrócony o kąt pi * v wokół osi Y...
            tab[i][j][1] = y  # y: nie zależy od v -> każdy wiersz jest poziomym pierścieniem.
            tab[i][j][2] = radius * sin(pi * v)  # z: ...druga składowa tego samego obrotu.
    return tab  # Tablica gotowa do przekazania do glVertex3f().


def startup(window):  # Wykonywana raz, gdy kontekst OpenGL jest gotowy, przed główną pętlą.
    global vertices, colors  # Przypisujemy zmienne na poziomie modułu, a nie lokalne.
    width, height = glfwGetFramebufferSize(window)  # Rozmiar w PIKSELACH (na Retinie jest 2x większy niż rozmiar okna w punktach).
    update_viewport(window, width, height)  # Ustaw viewport i projekcję dla początkowego rozmiaru.
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Czarne tło.
    glEnable(GL_DEPTH_TEST)  # Bufor głębi: bliższe fragmenty zasłaniają dalsze niezależnie od kolejności rysowania.
    vertices = compute_egg(N)  # Oblicz model raz; render() tylko go odczytuje.
    colors = random_colors(N)  # Generowane raz, aby kolory nie migotały (nie są losowane od nowa w każdej klatce).


def shutdown():  # Wykonywana raz po zakończeniu głównej pętli; miejsce na zwolnienie zasobów OpenGL.
    pass  # Nic do zwolnienia w tym programie.


def axes():  # Rysuje prosty układ współrzędnych: X czerwony, Y zielony, Z niebieski.
    glBegin(GL_LINES)  # Każde 2 kolejne wierzchołki tworzą osobny odcinek.

    glColor3f(1.0, 0.0, 0.0)  # Czerwony dla osi X.
    glVertex3f(-5.0, 0.0, 0.0)  # Początek osi X.
    glVertex3f(5.0, 0.0, 0.0)  # Koniec osi X.

    glColor3f(0.0, 1.0, 0.0)  # Zielony dla osi Y.
    glVertex3f(0.0, -5.0, 0.0)  # Początek osi Y.
    glVertex3f(0.0, 5.0, 0.0)  # Koniec osi Y.

    glColor3f(0.0, 0.0, 1.0)  # Niebieski dla osi Z (skierowana na widza, więc ledwo widoczna).
    glVertex3f(0.0, 0.0, -5.0)  # Początek osi Z.
    glVertex3f(0.0, 0.0, 5.0)  # Koniec osi Z.

    glEnd()  # Zakończ odcinki.


def random_colors(n):  # Buduje tablicę n x n losowych kolorów RGB, po jednym na wierzchołek.
    return [[[random.random() for _ in range(3)] for _ in range(n)] for _ in range(n)]  # Każda ze składowych R, G, B to losowa liczba z [0, 1).


def draw_vertex(i, j):  # Wysyła wierzchołek (i, j) siatki razem z jego własnym kolorem.
    glColor3f(*colors[i][j])  # Najpierw ustaw kolor: glVertex bierze kolor bieżący w tej chwili.
    glVertex3f(*vertices[i][j])  # Potem pozycja [x, y, z] tego samego elementu siatki.


def draw_egg_triangles():  # Pokrywa każdą komórkę siatki dwoma trójkątami.
    glBegin(GL_TRIANGLES)  # Każde 3 kolejne wierzchołki tworzą osobny trójkąt.
    for i in range(N - 1):  # Komórki istnieją między wierszami i oraz i + 1, więc ostatni wiersz tylko zamyka komórki.
        for j in range(N - 1):  # Podobnie, komórki istnieją między kolumnami j oraz j + 1.
            draw_vertex(i, j)  # Trójkąt 1: element (i, j)...
            draw_vertex(i + 1, j)  # ...jego sąsiad w u (i + 1, j)...
            draw_vertex(i, j + 1)  # ...i jego sąsiad w v (i, j + 1).

            draw_vertex(i + 1, j)  # Trójkąt 2 (dopełniający): (i + 1, j)...
            draw_vertex(i + 1, j + 1)  # Trójkąt 2: przeciwległy róg (i + 1, j + 1)...
            draw_vertex(i, j + 1)  # ...oraz (i, j + 1); razem oba trójkąty wypełniają komórkę.
    glEnd()  # Zakończ wszystkie trójkąty.


def spin(angle):  # Obraca wszystko rysowane później o "angle" stopni wokół X, potem Y, potem Z.
    glRotatef(angle, 1.0, 0.0, 0.0)  # Obrót o kąt (w stopniach) wokół osi X (wektor [1, 0, 0]).
    glRotatef(angle, 0.0, 1.0, 0.0)  # Obrót o kąt (w stopniach) wokół osi Y (wektor [0, 1, 0]).
    glRotatef(angle, 0.0, 0.0, 1.0)  # Obrót o kąt (w stopniach) wokół osi Z (wektor [0, 0, 1]).


def render(time):  # Rysuje jedną klatkę; "time" = sekundy od glfwInit(), napędza obrót.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Wyczyść kolory i głębie pozostałe z poprzedniej klatki.
    glLoadIdentity()  # Zresetuj macierz MODELVIEW, aby transformacje nie kumulowały się między klatkami.

    axes()  # Osie są rysowane przed spin(), więc stoją w miejscu, gdy model się obraca.
    spin(time * 180 / pi)  # Traktuj czas jako radiany i zamień na stopnie: pełny obrót co 2*pi sekund.
    draw_egg_triangles()  # Narysuj (obrócone) kolorowe jajko.

    glFlush()  # Wypchnij wszystkie zakolejkowane polecenia OpenGL do GPU w celu wykonania.


def update_viewport(window, width, height):  # Wywoływana na starcie i przy każdej zmianie rozmiaru framebuffera.
    if height == 0:  # Zminimalizowane okno może zgłosić wysokość 0...
        height = 1  # ...co spowodowałoby dzielenie przez zero poniżej, więc ograniczamy ją.
    if width == 0:  # To samo zabezpieczenie dla szerokości...
        width = 1  # ...aby proporcje obrazu zawsze były poprawną liczbą dodatnią.
    aspect_ratio = width / height  # Stosunek szerokości do wysokości, używany, by kształty nie były rozciągane.

    glMatrixMode(GL_PROJECTION)  # Kolejne wywołania macierzowe modyfikują macierz PROJEKCJI (odwzorowanie świat -> ekran).
    glViewport(0, 0, width, height)  # Odwzoruj wyjście OpenGL na cały framebuffer: x, y lewego dolnego rogu, szerokość, wysokość.
    glLoadIdentity()  # Zresetuj macierz MODELVIEW, aby transformacje nie kumulowały się między klatkami.

    if width <= height:  # Okno jest wysokie (lub kwadratowe): X zachowuje zakres [-7.5, 7.5]...
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)  # ...a Y jest rozszerzony; Z również [-7.5, 7.5].
    else:  # Okno jest szerokie: Y zachowuje zakres [-7.5, 7.5]...
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)  # ...a zamiast tego X jest rozszerzony.

    glMatrixMode(GL_MODELVIEW)  # Wróć do macierzy MODELVIEW (transformacje obiektów).
    glLoadIdentity()  # Zresetuj macierz MODELVIEW, aby transformacje nie kumulowały się między klatkami.


def main():  # Punkt wejścia programu: konfiguracja okna, główna pętla, sprzątanie.
    if not glfwInit():  # Zainicjuj bibliotekę GLFW; przy niepowodzeniu zwraca False...
        sys.exit(-1)  # ...a wtedy nic więcej nie możemy zrobić.

    window = glfwCreateWindow(400, 400, __file__, None, None)  # Okno 400x400 z tytułem równym ścieżce skryptu.
    if not window:  # Nie udało się utworzyć okna (lub kontekstu OpenGL)...
        glfwTerminate()  # ...zwolnij to, co zaalokował GLFW...
        sys.exit(-1)  # ...a wtedy nic więcej nie możemy zrobić.

    glfwMakeContextCurrent(window)  # Ustaw kontekst OpenGL tego okna jako cel wszystkich wywołań gl*.
    glfwSetFramebufferSizeCallback(window, update_viewport)  # Przelicz projekcję przy każdej zmianie rozmiaru.
    glfwSwapInterval(1)  # V-sync: zamieniaj bufory co najwyżej raz na odświeżenie monitora.

    startup(window)  # Jednorazowa inicjalizacja.
    while not glfwWindowShouldClose(window):  # Pętla trwa, dopóki użytkownik nie zamknie okna.
        render(glfwGetTime())  # Narysuj klatkę w tylnym buforze.
        glfwSwapBuffers(window)  # Pokaż tylny bufor na ekranie (podwójne buforowanie).
        glfwPollEvents()  # Obsłuż oczekujące zdarzenia bez czekania, aby pętla dalej renderowała klatki.
    shutdown()  # Jednorazowe sprzątanie.

    glfwTerminate()  # ...zwolnij to, co zaalokował GLFW...


if __name__ == '__main__':  # Uruchom main() tylko przy bezpośrednim wykonaniu, nie przy imporcie.
    main()  # Uruchom program.
