import pygame
import sys
import requests
import os

pygame.init()
screen = pygame.display.set_mode((600, 450))


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Button(pygame.sprite.Sprite):

    def __init__(self, x, y, image, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def begin():
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)
    text = "Введите адрес: "
    input_active = True
    running = True
    all_sprites = pygame.sprite.Group()
    button = Button(250, 300, pygame.transform.scale(load_image('search.png', -1), (100, 100)), all_sprites)
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                if button.rect.collidepoint(x, y):
                    running = False

            screen.fill(0)
            all_sprites.draw(screen)
            all_sprites.update()
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, text_surf.get_rect(center=screen.get_rect().center))
            pygame.display.flip()

    pygame.quit()
    return text.split(': ')[1]


def draw(screen, full_address):
    font = pygame.font.Font(None, 25)
    text = font.render(full_address, True, (0, 0, 0))
    text_x = 70
    text_y = 15
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 0, 0), (text_x - 10, text_y - 10,
                                         text_w + 20, text_h + 20), 5)


def show_map(ll_spn, pt, zn, all_sprites, full_address, post, map_type="map"):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={ll_spn}&l={map_type}&spn={zn},{zn}&pt={pt}"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(map_file), (0, 0))
    all_sprites.draw(screen)
    if post:
        draw(screen, full_address[0] + ', почтовый индекс: ' + full_address[1])
    else:
        draw(screen, full_address[0])

    pygame.display.flip()


def find_address(coords):
    API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
    geocoder_api_server = geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}" \
                                             f"&geocode={coords}&format=json"
    response = requests.get(geocoder_api_server).json()
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    return toponym['metaDataProperty']['GeocoderMetaData']['text']


def find_coords_and_full_addr(address):
    API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
    geocoder_api_server = geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}" \
                                             f"&geocode={address}&format=json"
    response = requests.get(geocoder_api_server).json()
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    coords = list(map(float, toponym_coodrinates.split(' ')))
    try:
        return coords, toponym['metaDataProperty']['GeocoderMetaData']['text'], \
               toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
    except Exception:
        return coords, toponym['metaDataProperty']['GeocoderMetaData']['text'], 'no postal code'


def main(flag):
    address = begin()
    coords, full_address, post_addr = find_coords_and_full_addr(address)
    const = [coords[0], coords[1]]
    if flag:
        print('Чтобы поменять вид карты на схему, нажмите на клавишу английской A')
        print('Чтобы поменять вид карты на спутник, нажмите на клавишу английской S')
        print('Чтобы поменять вид карты на гибрид, нажмите на клавишу английской D')
    full_addr = [full_address, post_addr]
    post = True
    running = True
    z = 0.03
    all_sprites = pygame.sprite.Group()
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    button = Button(0, 0, pygame.transform.scale(load_image('reset.png', -1), (50, 50)), all_sprites)
    post_button = Button(0, 50, pygame.transform.scale(load_image('post.png', -1), (50, 50)), all_sprites)
    show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites, full_addr, post)
    map_type = 'map'
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    if z < 0.1:
                        z += 0.01
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_PAGEDOWN:
                    if z - 0.01 > 0:
                        z -= 0.01
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_UP:
                    if coords[1] < 55.87:
                        coords[1] += z / 2
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_DOWN:
                    if coords[1] > 55.75:
                        coords[1] -= z / 2
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_LEFT:
                    if coords[0] > 37.68:
                        coords[0] -= z / 2
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_RIGHT:
                    if coords[0] < 37.8:
                        coords[0] += z / 2
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_a:
                    if map_type != 'map':
                        map_type = 'map'
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_s:
                    if map_type != 'sat':
                        map_type = 'sat'
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
                elif event.key == pygame.K_d:
                    if map_type != 'sat,skl':
                        map_type = 'sat,skl'
                        pygame.quit()
                        os.remove('map.png')
                        show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                                 full_addr, post,
                                 map_type)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x = event.pos[0]
                y = event.pos[1]
                shir_0 = coords[1] - z
                dol_0 = coords[0] - z
                shir_m = shir_0 + ((450 - y) * z * 2 / 450)
                dol_m = dol_0 + (x * z * 2 / 600)
                address = find_address(f'{dol_m},{shir_m}')
                print(address)
                new_coords, full_address, post_addr = find_coords_and_full_addr(address)
                full_addr = [full_address, post_addr]
                const = [dol_m, shir_m]
                show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                         full_addr, post)
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                if button.rect.collidepoint(x, y):
                    running = False
                elif post_button.rect.collidepoint(x, y):
                    if post:
                        post = False
                    else:
                        post = True
                    pygame.quit()
                    os.remove('map.png')
                    show_map(','.join(list(map(str, coords))), ','.join(list(map(str, const))), str(z), all_sprites,
                             full_addr,
                             post,
                             map_type)
    main(False)


if __name__ == "__main__":
    main(True)
