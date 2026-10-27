#!/usr/bin/env python3
# Zadanie 1 (ocena 3.0): model jajka zbudowany z punktów (GL_POINTS).
# Użycie: uv run lab3/zad1_egg_points.py [N]   (N = liczba próbek na parametr, domyślnie 20)

import sys  # sys.exit() przy błędach krytycznych oraz sys.argv dla parametru N z wiersza poleceń.
from math import cos, sin, pi  # Trygonometria do równań parametrycznych; pi dla zakresu kątów.

from glfw.GLFW import *  # GLFW: tworzy okno i kontekst OpenGL oraz obsługuje zdarzenia wejścia (nazwy w stylu C).

from OpenGL.GL import *  # Podstawowe funkcje OpenGL (gl*) i stałe (GL_*).
from OpenGL.GLU import *  # Biblioteka pomocnicza OpenGL (glu*); jeszcze nieużywana, zostaje dla zgodności z szablonem z zajęć.

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20  # Liczba próbek u i v z 1. argumentu wiersza poleceń; N x N wierzchołków.

vertices = None  # Tablica N x N x 3 wierzchołków jajka; wypełniana raz w startup().


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
    global vertices  # Przypisujemy zmienną na poziomie modułu, a nie lokalną.
    width, height = glfwGetFramebufferSize(window)  # Rozmiar w PIKSELACH (na Retinie jest 2x większy niż rozmiar okna w punktach).
    update_viewport(window, width, height)  # Ustaw viewport i projekcję dla początkowego rozmiaru.
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Czarne tło, aby żółte punkty były dobrze widoczne.
    glEnable(GL_DEPTH_TEST)  # Bufor głębi: bliższe fragmenty zasłaniają dalsze niezależnie od kolejności rysowania.
    vertices = compute_egg(N)  # Oblicz model raz; render() tylko go odczytuje.


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


def draw_egg_points():  # Rysuje każdy wierzchołek jajka jako pojedynczy punkt.
    glColor3f(1.0, 1.0, 0.0)  # Żółty; bieżący kolor jest używany przez wszystkie kolejne wierzchołki.
    glBegin(GL_POINTS)  # Każdy wierzchołek jest rysowany jako osobny punkt.
    for row in vertices:  # Każdy wiersz = jedna wartość u = jeden poziomy pierścień jajka.
        for vertex in row:  # Każdy wierzchołek w pierścieniu = jedna wartość v.
            glVertex3f(*vertex)  # Rozpakuj [x, y, z] na trzy argumenty glVertex3f.
    glEnd()  # Zakończ punkty.


def render(time):  # Rysuje jedną klatkę; "time" = sekundy od glfwInit() (tu nieużywane).
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Wyczyść kolory i głębie pozostałe z poprzedniej klatki.
    glLoadIdentity()  # Zresetuj macierz MODELVIEW, aby transformacje nie kumulowały się między klatkami.

    axes()  # Najpierw układ współrzędnych...
    draw_egg_points()  # ...potem jajko.

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

    if width <= height:  # Okno jest wysokie (lub kwadratowe): X zachowuje zakres [-7.5, 7.5]...
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)  # ...a Y jest rozszerzony; Z również [-7.5, 7.5].
    else:  # Okno jest szerokie: Y zachowuje zakres [-7.5, 7.5]...
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)  # ...a zamiast tego X jest rozszerzony.

    glMatrixMode(GL_MODELVIEW)  # Wróć do macierzy MODELVIEW (transformacje obiektów).
    glLoadIdentity()  # Zacznij bez transformacji obiektu.


def main():  # Punkt wejścia programu: konfiguracja okna, główna pętla, sprzątanie.
    if not glfwInit():  # Zainicjuj bibliotekę GLFW; przy niepowodzeniu zwraca False...
        sys.exit(-1)  # ...a wtedy nic więcej nie możemy zrobić.

    window = glfwCreateWindow(400, 400, __file__, None, None)  # Okno 400x400 z tytułem równym ścieżce skryptu.
    if not window:  # Nie udało się utworzyć okna (lub kontekstu OpenGL)...
        glfwTerminate()  # ...zwolnij to, co zaalokował GLFW...
        sys.exit(-1)  # ...i zakończ z kodem błędu.

    glfwMakeContextCurrent(window)  # Ustaw kontekst OpenGL tego okna jako cel wszystkich wywołań gl*.
    glfwSetFramebufferSizeCallback(window, update_viewport)  # Przelicz projekcję przy każdej zmianie rozmiaru.
    glfwSwapInterval(1)  # V-sync: zamieniaj bufory co najwyżej raz na odświeżenie monitora.

    startup(window)  # Jednorazowa inicjalizacja.
    while not glfwWindowShouldClose(window):  # Pętla trwa, dopóki użytkownik nie zamknie okna.
        render(glfwGetTime())  # Narysuj klatkę w tylnym buforze.
        glfwSwapBuffers(window)  # Pokaż tylny bufor na ekranie (podwójne buforowanie).
        glfwPollEvents()  # Obsłuż oczekujące zdarzenia bez czekania, aby pętla dalej renderowała klatki.
    shutdown()  # Jednorazowe sprzątanie.

    glfwTerminate()  # Zniszcz okno i zwolnij zasoby GLFW.


if __name__ == '__main__':  # Uruchom main() tylko przy bezpośrednim wykonaniu, nie przy imporcie.
    main()  # Uruchom program.
