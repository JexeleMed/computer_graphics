#!/usr/bin/env python3
# Zadanie 3 (ocena 4.0): prostokąt z losowymi kolorami wierzchołków i losową deformacją sterowaną parametrem d.

import sys  # Moduł standardowy, użyty tu tylko do sys.exit() przy błędach krytycznych.
import random  # Standardowy generator liczb pseudolosowych.

from glfw.GLFW import *  # GLFW: tworzy okno i kontekst OpenGL oraz obsługuje zdarzenia wejścia (nazwy w stylu C).

from OpenGL.GL import *  # Podstawowe funkcje OpenGL (gl*) i stałe (GL_*).
from OpenGL.GLU import *  # Biblioteka pomocnicza OpenGL (glu*); jeszcze nieużywana, zostaje dla zgodności z szablonem z zajęć.


def startup(window):  # Wykonywana raz, gdy kontekst OpenGL jest gotowy, przed główną pętlą.
    width, height = glfwGetFramebufferSize(window)  # Rozmiar w PIKSELACH (na Retinie jest 2x większy niż rozmiar okna w punktach).
    update_viewport(window, width, height)  # Ustaw viewport i projekcję dla początkowego rozmiaru.
    glClearColor(0.5, 0.5, 0.5, 1.0)  # Kolor używany przez glClear(): RGBA, każda składowa 0.0-1.0 -> średnia szarość, w pełni nieprzezroczysta.


def shutdown():  # Wykonywana raz po zakończeniu głównej pętli; miejsce na zwolnienie zasobów OpenGL.
    pass  # Nic do zwolnienia w tym programie.


def random_color():  # Zwraca losowy kolor RGB jako krotkę 3 liczb zmiennoprzecinkowych.
    return (random.random(), random.random(), random.random())  # random.random() zwraca wartości z [0.0, 1.0) - dokładnie zakres glColor3f.


def draw_rectangle(x, y, a, b, d=0.0):  # Środek (x, y), szerokość a, wysokość b; d = stopień deformacji (0.0 = idealny prostokąt).
    half_a = a / 2.0  # Połowa szerokości.
    half_b = b / 2.0  # Połowa wysokości.

    corners = [  # 4 rogi niezdeformowanego prostokąta, przeciwnie do ruchu wskazówek zegara od lewego dolnego.
        [x - half_a, y - half_b],  # 0: lewy dolny.
        [x + half_a, y - half_b],  # 1: prawy dolny.
        [x + half_a, y + half_b],  # 2: prawy górny.
        [x - half_a, y + half_b],  # 3: lewy górny.
    ]  # Listy (nie krotki), aby współrzędne dało się zmieniać poniżej.

    for corner in corners:  # Deformacja: przesuń każdy róg o losowe przesunięcie.
        corner[0] += random.uniform(-d, d) * a  # Przesuń X o co najwyżej d * szerokość w dowolnym kierunku.
        corner[1] += random.uniform(-d, d) * b  # Przesuń Y o co najwyżej d * wysokość w dowolnym kierunku.

    colors = [random_color() for _ in corners]  # Jeden losowy kolor na róg (rogi wspólne dla trójkątów zachowują ten sam kolor).

    glBegin(GL_TRIANGLES)  # 6 wierzchołków -> 2 trójkąty.
    for index in (0, 1, 3, 1, 2, 3):  # Trójkąt (0,1,3) i trójkąt (1,2,3); mają wspólną przekątną 1-3.
        glColor3f(*colors[index])  # Ustaw kolor tego rogu; "*" rozpakowuje krotkę na 3 argumenty.
        glVertex2f(*corners[index])  # Wyślij róg; "*" rozpakowuje [x, y] na 2 argumenty.
    glEnd()  # Zakończ; kolory są interpolowane w obrębie każdego trójkąta.


def render(time):  # Rysuje jedną klatkę; "time" = sekundy od glfwInit() (tu nieużywane).
    glClear(GL_COLOR_BUFFER_BIT)  # Wypełnij cały bufor koloru kolorem czyszczenia.

    random.seed(2137)  # To samo ziarno w każdej klatce -> te same "losowe" liczby -> obraz nie migocze przy przerysowaniu/zmianie rozmiaru.

    draw_rectangle(-45.0, 45.0, 70.0, 50.0)  # d domyślnie 0.0: losowe kolory, bez deformacji.
    draw_rectangle(45.0, 45.0, 70.0, 50.0, 0.1)  # Lekka deformacja.
    draw_rectangle(-45.0, -45.0, 70.0, 50.0, 0.2)  # Silniejsza deformacja.
    draw_rectangle(45.0, -45.0, 70.0, 50.0, 0.35)  # Silna deformacja (trójkąty mogą zacząć się zawijać).

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

    window = glfwCreateWindow(400, 400, __file__, None, None)  # Okno 400x400 z tytułem równym ścieżce tego pliku; bez monitora pełnoekranowego i bez współdzielonego kontekstu.
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
