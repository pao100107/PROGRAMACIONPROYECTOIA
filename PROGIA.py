import random, pygame, sys

primera_celda_pulsada = True
calidades_casilla = {} # numero de casilla = [indice (x, y) posicion en el tablero, posicion (x,y) en la pantalla, valor, pulsada (true o false)]

bombas_restantes = 0
bombas_correctas = 0

def crear_cuadricula(numero, tamaño_cuadricua):
    global ventana, font, cuadricula, tamano_cuadricula
    cuadricula = []
    
    # Crear un triángulo en lugar de una matriz cuadrada
    for row in range(numero):
        linea = [0] * (row + 1)
        cuadricula.append(linea)
    
    tamano_cuadricula = tamaño_cuadricua
    medidas = int((numero * (numero + 1)) / 2 * tamano_cuadricula)
    ventana = pygame.display.set_mode((medidas + 100, medidas))
    
    font = pygame.font.Font(None, tamano_cuadricula)

    i = 0
    for row in range(len(cuadricula)):
        for col in range(len(cuadricula[row])):
            # Ajustar las coordenadas para dibujar un triángulo
            square_rect = pygame.Rect(2 + (col * tamano_cuadricula), 2 + (row * tamano_cuadricula), tamano_cuadricula - 4, tamano_cuadricula - 4)
            pygame.draw.rect(ventana, 'black', square_rect.inflate(2,2))
            pygame.draw.rect(ventana, 'white', square_rect)
            pygame.display.update()
            calidades_casilla[i] = {'numero': i, 'indice': (row, col), 'posicion_xy': square_rect, 'valor': ' ', 'pulsada': False, 'bandera': False}
            i += 1

    return cuadricula

def crear_bombas_random(numero, primer_click, dificultad):
    global cuadricula, bombas_correctas
    bombas = int((numero * (numero + 1) // 2) * dificultad)
    bombas_correctas = bombas
    
    while bombas > 0:
        random_row = random.randint(0, numero - 1)
        random_col = random.randint(0, random_row)
        
        # Verificar si la posición aleatoria está dentro de la región 3x3 alrededor del primer_click
        if abs(random_row - primer_click[0]) <= 1 and abs(random_col - primer_click[1]) <= 1:
            continue
        
        # Si la posición no está en la región 3x3 alrededor de primer_click y está vacía (0)
        if cuadricula[random_row][random_col] == 0:
            cuadricula[random_row][random_col] = 'b'
            bombas -= 1
            donde_ahy_bomba()  # Mover la llamada aquí
    
    # Llamar a donde_ahy_bomba una vez más después de salir del bucle while
    donde_ahy_bomba()


def donde_ahy_bomba():
    indice = 0
    for row in range(len(cuadricula)):
        for col in range(len(cuadricula[row])):
            bombas_alrededor = 0
            
            # Verificar celdas adyacentes en forma de triángulo
            for i in range(max(0, row - 1), min(row + 2, len(cuadricula))):
                for j in range(max(0, col - 1), min(col + 2, i + 1)):
                    if i == row and j == col:
                        continue
                    
                    try:
                        if cuadricula[i][j] == 'b':
                            bombas_alrededor += 1
                    except IndexError:
                        pass
            
            if cuadricula[row][col] != 'b':
                cuadricula[row][col] = bombas_alrededor
                calidades_casilla[indice]['valor'] = cuadricula[row][col]
            indice += 1  

def color_numero(element,color):
    valor_casilla = font.render(str(calidades_casilla[element]['valor']),True,color)
    ventana.blit(valor_casilla,(calidades_casilla[element]['posicion_xy'].x + (tamano_cuadricula / 4),calidades_casilla[element]['posicion_xy'].y + (tamano_cuadricula / 8)))
    pygame.display.update()

def revelar_casillas_adyacentes(numero, indice):
    row, col = indice
    for i in range(max(0, row - 1), min(row + 2, numero)):
        for j in range(max(0, col - 1), min(col + 2, len(cuadricula[i]))):
            if not calidades_casilla[i * (i + 1) // 2 + j]['pulsada']:
                valor = calidades_casilla[i * (i + 1) // 2 + j]['valor']
                if valor == 0:
                    color_numero(i * (i + 1) // 2 + j, (0, 0, 255))
                    calidades_casilla[i * (i + 1) // 2 + j]['pulsada'] = True
                    revelar_casillas_adyacentes(numero, (i, j))
                elif isinstance(valor, int) and valor > 0:
                    color_numero(i * (i + 1) // 2 + j, (255, 255, 255))
                    calidades_casilla[i * (i + 1) // 2 + j]['pulsada'] = True



def click_casilla(numero, event, dificultad):
    global primera_celda_pulsada, bombas_restantes, bombas_correctas
    for element in calidades_casilla:
        if calidades_casilla[element]['posicion_xy'].collidepoint(event.pos):
            if primera_celda_pulsada:
                print(calidades_casilla[element]['indice'])
                crear_bombas_random(numero, calidades_casilla[element]['indice'], dificultad)
                primera_celda_pulsada = False
            if not primera_celda_pulsada:
                keys = pygame.mouse.get_pressed()
                if keys[0] and not calidades_casilla[element]['bandera']:
                    valor = calidades_casilla[element]['valor']
                    if valor == 0:
                        color_numero(element, (0, 0, 255))
                    elif valor == 'b':
                        color_numero(element, (255, 0, 0))  # Revelar la mina en rojo
                        pygame.display.update()
                        return False, True  # El jugador ha perdido
                    else:
                        # Revelar las casillas adyacentes si el valor no es 0
                        revelar_casillas_adyacentes(numero, calidades_casilla[element]['indice'])
                        color_numero(element, (255, 255, 255))  # Ajusta los colores según el valor de la celda
                        calidades_casilla[element]['pulsada'] = True


                if keys[2]:
                    if not calidades_casilla[element]['pulsada'] == True and not calidades_casilla[element]['bandera'] == True and not bombas_restantes == 0:
                        valor_casilla = font.render('?', True, (0, 0, 0))
                        ventana.blit(valor_casilla, (calidades_casilla[element]['posicion_xy'].x + 10, calidades_casilla[element]['posicion_xy'].y + 5))
                        pygame.display.update()
                        calidades_casilla[element]['bandera'] = True
                        bombas_restantes -= 1

                    elif not calidades_casilla[element]['pulsada'] == True and not calidades_casilla[element]['bandera'] == False:
                        square_rect = pygame.Rect(calidades_casilla[element]['posicion_xy'].x, calidades_casilla[element]['posicion_xy'].y, tamano_cuadricula - 4, tamano_cuadricula - 4)
                        pygame.draw.rect(ventana, 'white', square_rect)
                        pygame.display.update()
                        calidades_casilla[element]['bandera'] = False
                        bombas_restantes += 1

                    if calidades_casilla[element]['valor'] == 'b' and calidades_casilla[element]['bandera'] == True:
                        bombas_correctas -= 1
                        if bombas_correctas == 0:
                            return True, False

    return False, False



def menu():
    pygame.init()

    menu_active = True
    font = pygame.font.Font(None, 50)

    screen = pygame.display.set_mode((400,300))

    easy_button = pygame.Rect(100, 0, 200, 80)
    normal_button = pygame.Rect(100, 100, 200, 80)
    hard_button = pygame.Rect(100, 200, 200, 80)

    BLACK_COLOR = (0,0,0)
    WHITE_COLOR = (255,255,255)
    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    numero = 5
                    dificultad = .3
                    casillas = 40
                    return numero, dificultad, casillas
                elif normal_button.collidepoint(event.pos):
                    numero = 10
                    dificultad = .5
                    casillas = 40
                    return numero, dificultad, casillas
                elif hard_button.collidepoint(event.pos):
                    numero = 15
                    dificultad = .7
                    casillas = 40
                    return numero, dificultad, casillas
			
            pygame.draw.rect(screen, BLACK_COLOR, easy_button)
            pygame.draw.rect(screen, BLACK_COLOR, normal_button) 
            pygame.draw.rect(screen, BLACK_COLOR, hard_button)   
			
            start_text = font.render("EASY", True, WHITE_COLOR)			
            screen.blit(start_text, (easy_button.x + 40, easy_button.y + 20))

            start_text = font.render("NORMAL", True, WHITE_COLOR)			
            screen.blit(start_text, (normal_button.x + 40, normal_button.y + 20))

            start_text = font.render("HARD", True, WHITE_COLOR)			
            screen.blit(start_text, (hard_button.x + 40, hard_button.y + 20))
                	

            pygame.display.update()

def mostrar_bombas(numero,casillas):
    global bombas_restantes
    x = numero * casillas + 50
    y = 0
    pygame.draw.rect(ventana, (0,0,0), (x,y,100,100))
    font = pygame.font.Font(None,60)
    start_text = font.render(str(bombas_restantes), True, (255,255,255))			
    ventana.blit(start_text, (x,y))
    pygame.display.update()

def game(numero,dificultad,casillas):
    global primera_celda_pulsada, calidades_casilla, bombas_restantes
    ganar, perder = False, False
    while not ganar and not perder:
        for event in pygame.event.get():
            mostrar_bombas(numero,casillas)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ganar, perder =  click_casilla(numero,event,dificultad)
    primera_celda_pulsada = True
    calidades_casilla = {}
    bombas_restantes = 0
    run()
    
def run():
    global bombas_restantes
    numero,dificultad,casillas = menu()
    crear_cuadricula(numero,casillas)
    bombas_iniciales = int(numero * numero * dificultad)
    bombas_restantes = bombas_iniciales
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game(numero,dificultad,casillas)

if _name_ == '_main_':
   run()
