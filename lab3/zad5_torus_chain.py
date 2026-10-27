#!/usr/bin/env python3
# Zadanie 5 (ocena 5.0), praca domowa 3.3: łańcuch z torusów, ułożony wzdłuż zamkniętej falistej krzywej.
# Sąsiednie ogniwa są obrócone o 90 stopni wokół stycznej do krzywej, więc zazębiają się.
# Użycie: uv run lab3/zad5_torus_chain.py

import sys  # sys.exit() przy błędach krytycznych.
import colorsys  # hsv_to_rgb(): prosty sposób na tęczę kolorów wzdłuż łańcucha.
from math import cos, sin, sqrt, pi  # Trygonometria dla krzywej i torusa; sqrt do długości wektorów.

from glfw.GLFW import *  # GLFW: tworzy okno i kontekst OpenGL oraz obsługuje zdarzenia wejścia (nazwy w stylu C).

from OpenGL.GL import *  # Podstawowe funkcje OpenGL (gl*) i stałe (GL_*).
from OpenGL.GLU import *  # Biblioteka pomocnicza OpenGL (glu*); jeszcze nieużywana, zostaje dla zgodności z szablonem z zajęć.

MAJOR_RADIUS = 0.6  # R: odległość od środka ogniwa do środka jego rury.
MINOR_RADIUS = 0.13  # r: promień rury (grubość drutu).
U_SAMPLES = 16  # Próbki u = kąt wokół dużego okręgu jednego ogniwa.
V_SAMPLES = 10  # Próbki v = kąt wokół rury.
LIGHT = (0.4, 0.8, 0.45)  # Kierunek do sztucznego źródła światła, używany tylko do cieniowania kolorów wierzchołków.

chain_list = None  # ID listy wyświetlania OpenGL zawierającej cały łańcuch; tworzone w startup().


def curve(t):  # Zamknięta krzywa, wzdłuż której biegnie łańcuch, t w [0, 2*pi].
    return 5.0 * cos(t), 1.0 * sin(3 * t), 5.0 * sin(t)  # Okrąg o promieniu 5 w płaszczyźnie XZ, falujący w górę i w dół 3 razy.


def normalize(vector):  # Zwraca wektor przeskalowany do długości 1.
    length = sqrt(sum(c * c for c in vector))  # Długość euklidesowa sqrt(x^2 + y^2 + z^2).
    return tuple(c / length for c in vector)  # Podziel każdą składową przez długość.


def cross(a, b):  # Iloczyn wektorowy a x b: wektor prostopadły do a i b.
    return a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]  # Standardowy wzór.


def link_frames():  # Oblicza pozycję i orientację każdego ogniwa wzdłuż krzywej.
    samples = 2000  # Krzywa jest aproksymowana 2000 krótkich odcinków, aby zmierzyć jej długość.
    params = [2 * pi * k / samples for k in range(samples + 1)]  # Wartości t od dokładnie 0 do dokładnie 2*pi.
    points = [curve(t) for t in params]  # Punkty na krzywej dla tych wartości t.
    lengths = [0.0]  # lengths[k] = długość łuku od początku krzywej do points[k].
    for p, q in zip(points, points[1:]):  # Każda para kolejnych punktów = jeden krótki odcinek...
        lengths.append(lengths[-1] + sqrt(sum((a - b) ** 2 for a, b in zip(p, q))))  # ...dodaje jego długość do sumy.

# Zazębione pierścienie wymagają odstępu środków poniżej 2 * (R - r); parzysta liczba ogniw domyka naprzemienny łańcuch.
    count = round(lengths[-1] / (2 * (MAJOR_RADIUS - MINOR_RADIUS) - 0.1))  # Liczba ogniw: całkowita długość / odstęp.
    count += count % 2  # Zrób ją parzystą, aby ostatnie ogniwo (nieparzyste) i pierwsze (parzyste) były prostopadłe.
    spacing = lengths[-1] / count  # Dokładny odstęp dzielący zamkniętą krzywą równo -> łańcuch się domyka.

    frames = []  # Jedna krotka (środek, pierwsza oś w płaszczyźnie, druga oś w płaszczyźnie, oś torusa) na ogniwo.
    k = 0  # Indeks bieżącej próbki krzywej; tylko rośnie, bo ogniwa są odwiedzane po kolei.
    for link in range(count):  # Dla każdego ogniwa...
        while lengths[k + 1] < link * spacing:  # ...idź wzdłuż krzywej, aż osiągniesz jego długość łuku...
            k += 1  # ...po jednej próbce naraz.
        t = params[k]  # Parametr krzywej środka tego ogniwa.
        center = curve(t)  # Środek ogniwa leży na krzywej.
        tangent = normalize(tuple(b - a for a, b in zip(curve(t - 1e-4), curve(t + 1e-4))))  # Kierunek krzywej.
        up = (0.0, 1.0, 0.0)  # Wektor odniesienia "w górę" używany do zbudowania układu wokół stycznej.
        dot = sum(a * b for a, b in zip(up, tangent))  # Część wektora "w górę" skierowana wzdłuż stycznej...
        normal = normalize(tuple(a - dot * b for a, b in zip(up, tangent)))  # ...jest usuwana -> normalna jest do niej prostopadła.
        binormal = cross(tangent, normal)  # Trzecia oś, prostopadła do stycznej i normalnej.
        if link % 2 == 0:  # Parzyste ogniwa...
            frames.append((center, tangent, normal, binormal))  # ...leżą w płaszczyźnie (styczna, normalna): pierścienie "stojące".
        else:  # Nieparzyste ogniwa...
            frames.append((center, tangent, binormal, normal))  # ...leżą w płaszczyźnie (styczna, binormalna): pierścienie "leżące".
    return frames  # Gotowe do zamiany na geometrię torusów.


def torus_link(center, first, second, axis, color):  # Wierzchołki i kolory jednego torusa o zadanym układzie.
    vertices = [[None] * V_SAMPLES for _ in range(U_SAMPLES)]  # Tablica U_SAMPLES x V_SAMPLES punktów [x, y, z].
    colors = [[None] * V_SAMPLES for _ in range(U_SAMPLES)]  # Tablica kolorów RGB tego samego rozmiaru.
    for i in range(U_SAMPLES):  # Indeks wiersza i <-> parametr u.
        u = i / (U_SAMPLES - 1)  # u od dokładnie 0.0 do dokładnie 1.0, aby pierścień się domknął.
        radial = tuple(cos(2 * pi * u) * a + sin(2 * pi * u) * b for a, b in zip(first, second))  # Wektor jednostkowy od środka ogniwa w stronę rury, w płaszczyźnie ogniwa.
        for j in range(V_SAMPLES):  # Indeks kolumny j <-> parametr v.
            v = j / (V_SAMPLES - 1)  # v od dokładnie 0.0 do dokładnie 1.0, aby rura się domknęła.
            ring = MAJOR_RADIUS + MINOR_RADIUS * cos(2 * pi * v)  # Odległość od środka ogniwa (R + r cos 2*pi*v), jak w równaniu torusa.
            vertices[i][j] = tuple(c + ring * r + MINOR_RADIUS * sin(2 * pi * v) * a  # środek + ta odległość wzdłuż "radial" + r sin 2*pi*v wzdłuż osi...
                                   for c, r, a in zip(center, radial, axis))  # ...policzone naraz dla x, y i z.
            normal = tuple(cos(2 * pi * v) * r + sin(2 * pi * v) * a for r, a in zip(radial, axis))  # Kierunek, w który zwrócona jest powierzchnia w tym punkcie.
# Proste sztuczne oświetlenie zapisane w kolorach wierzchołków, aby okrągły kształt był widoczny.
            shade = 0.3 + 0.7 * max(0.0, sum(n * l for n, l in zip(normal, normalize(LIGHT))))  # Jaśniej tam, gdzie powierzchnia jest zwrócona do światła; minimum 0.3.
            colors[i][j] = tuple(c * shade for c in color)  # Bazowy kolor ogniwa przyciemniony o cień.
    return vertices, colors  # Geometria jednego ogniwa.


def draw_link(vertices, colors):  # Rysuje jedno ogniwo, jeden pas trójkątów na warstwę, jak jajko w zadaniu 4.
    for i in range(U_SAMPLES - 1):  # U_SAMPLES - 1 warstw: między wierszem i a wierszem i + 1.
        glBegin(GL_TRIANGLE_STRIP)  # Każdy nowy wierzchołek tworzy trójkąt z 2 poprzednimi.
        for j in range(V_SAMPLES):  # Obejdź całą rurę, łącznie z ostatnią kolumną, aby ją domknąć.
            glColor3f(*colors[i][j])  # Kolor wierzchołka (i, j)...
            glVertex3f(*vertices[i][j])  # ...i jego pozycja: parzysty indeks w pasie, wiersz i.
            glColor3f(*colors[i + 1][j])  # Kolor wierzchołka (i + 1, j)...
            glVertex3f(*vertices[i + 1][j])  # ...i jego pozycja: nieparzysty indeks w pasie, wiersz i + 1 (zygzak).
        glEnd()  # Zakończ pas tej warstwy.


def startup(window):  # Wykonywana raz, gdy kontekst OpenGL jest gotowy, przed główną pętlą.
    global chain_list  # Przypisujemy zmienną na poziomie modułu, a nie lokalną.
    width, height = glfwGetFramebufferSize(window)  # Rozmiar w PIKSELACH (na Retinie jest 2x większy niż rozmiar okna w punktach).
    update_viewport(window, width, height)  # Ustaw viewport i projekcję dla początkowego rozmiaru.
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Czarne tło.
    glEnable(GL_DEPTH_TEST)  # Bufor głębi: bliższe fragmenty zasłaniają dalsze, więc zazębione ogniwa wyglądają poprawnie.

    frames = link_frames()  # Pozycja i orientacja każdego ogniwa.
# Lista wyświetlania: geometria jest wysyłana raz i odtwarzana w każdej klatce (dużo szybciej w Pythonie).
    chain_list = glGenLists(1)  # Zarezerwuj jeden identyfikator listy wyświetlania.
    glNewList(chain_list, GL_COMPILE)  # Rozpocznij nagrywanie: kolejne wywołania rysujące gl* są zapisywane, a nie wykonywane.
    for link, (center, first, second, axis) in enumerate(frames):  # Dla każdego ogniwa i jego układu...
        color = colorsys.hsv_to_rgb(link / len(frames), 0.6, 1.0)  # ...wybierz odcień, który okrąża koło barw wzdłuż łańcucha...
        draw_link(*torus_link(center, first, second, axis, color))  # ...zbuduj jego torus i nagraj jego rysowanie.
    glEndList()  # Zakończ nagrywanie.


def shutdown():  # Wykonywana raz po zakończeniu głównej pętli; miejsce na zwolnienie zasobów OpenGL.
    glDeleteLists(chain_list, 1)  # Zwolnij listę wyświetlania utworzoną w startup().


def render(time):  # Rysuje jedną klatkę; "time" = sekundy od glfwInit(), napędza obrót.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Wyczyść kolory i głębie pozostałe z poprzedniej klatki.
    glLoadIdentity()  # Zresetuj macierz MODELVIEW, aby transformacje nie kumulowały się między klatkami.

    glRotatef(35.0, 1.0, 0.0, 0.0)  # Przechyl scenę o 35 stopni wokół X, aby łańcuch był widoczny pod kątem.
    glRotatef(time * 20.0, 0.0, 1.0, 0.0)  # Powoli obracaj wokół Y: 20 stopni na sekundę.
    glCallList(chain_list)  # Odtwórz nagrany łańcuch.

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
