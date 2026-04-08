import pygame
import random
import os
pygame.init()

# Ukuran layar dan FPS (Frame Per Second)
LEBAR, TINGGI = 800, 800
Layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("Cube Catcher - Project PBO dengan Gambar")
Jam = pygame.time.Clock()

# Definisi Warna (Warna fallback/cadangan jika gambar tidak ditemukan)
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
BIRU_FALLBACK = (50, 150, 255)
MERAH_FALLBACK = (255, 50, 50)
KUNING_FALLBACK = (255, 200, 0)

# Definisi Ukuran Konsisten untuk Gambar (Scale)
UKURAN_PLAYER = (80, 50)
UKURAN_BOMB = (40, 40)
UKURAN_COIN = (30, 30)


# Fungsi Helper untuk memuat gambar dengan aman
def muat_gambar_sprite(nama_file, ukuran, warna_fallback):
    folder_saat_ini = os.path.abspath(os.path.dirname(__file__))
    path_lengkap = os.path.join(folder_saat_ini, nama_file)

    try:
        if os.path.exists(path_lengkap):
            # Convert normal digunakan untuk background, convert_alpha untuk sprite transparan
            if nama_file == "bg.png":
                gambar = pygame.image.load(path_lengkap).convert()
            else:
                gambar = pygame.image.load(path_lengkap).convert_alpha()

            gambar = pygame.transform.scale(gambar, ukuran)
            return gambar
        else:
            raise FileNotFoundError
    except (pygame.error, FileNotFoundError):
        surface_fallback = pygame.Surface(ukuran)
        surface_fallback.fill(warna_fallback)
        return surface_fallback


# ==========================================
# 2. KONSEP PBO: CLASS & INHERITANCE
# ==========================================

class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_surface, x, y):
        super().__init__()
        self.image = image_surface
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(GameObject):
    def __init__(self):
        gambar_player = muat_gambar_sprite("bucket.png", UKURAN_PLAYER, BIRU_FALLBACK)
        super().__init__(gambar_player, LEBAR // 2, TINGGI - UKURAN_PLAYER[1] - 10)
        self.kecepatan = 8

    def update(self):
        tombol = pygame.key.get_pressed()
        if tombol[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.kecepatan
        if tombol[pygame.K_RIGHT] and self.rect.right < LEBAR:
            self.rect.x += self.kecepatan


class Bomb(GameObject):
    def __init__(self):
        gambar_bomb = muat_gambar_sprite("bomb.png", UKURAN_BOMB, MERAH_FALLBACK)
        x_acak = random.randint(0, LEBAR - UKURAN_BOMB[0])
        super().__init__(gambar_bomb, x_acak, random.randint(-150, -50))
        self.kecepatan = random.randint(4, 8)

    def update(self):
        self.rect.y += self.kecepatan
        if self.rect.top > TINGGI:
            self.reset_posisi()

    def reset_posisi(self):
        self.rect.y = random.randint(-150, -50)
        self.rect.x = random.randint(0, LEBAR - UKURAN_BOMB[0])
        self.kecepatan = random.randint(4, 8)


class Coin(GameObject):
    def __init__(self):
        gambar_coin = muat_gambar_sprite("coin.png", UKURAN_COIN, KUNING_FALLBACK)
        x_acak = random.randint(0, LEBAR - UKURAN_COIN[0])
        super().__init__(gambar_coin, x_acak, random.randint(-150, -50))
        self.kecepatan = 5

    def update(self):
        self.rect.y += self.kecepatan
        if self.rect.top > TINGGI:
            self.reset_posisi()

    def reset_posisi(self):
        self.rect.y = random.randint(-150, -50)
        self.rect.x = random.randint(0, LEBAR - UKURAN_COIN[0])


# ==========================================
# 3. SETUP OBJECT & GAME LOOP
# ==========================================

# --- FITUR BARU: Memuat Background ---
# Jika bg.png tidak ada, background akan otomatis menjadi warna HITAM
gambar_background = muat_gambar_sprite("bg.png", (LEBAR, TINGGI), HITAM)

semua_sprite = pygame.sprite.Group()
grup_bomb = pygame.sprite.Group()
grup_coin = pygame.sprite.Group()

player = Player()
semua_sprite.add(player)

# Pengaturan Rasio Bomb dan Coin (1:3)
JUMLAH_BOMB = 2
JUMLAH_COIN = JUMLAH_BOMB * 3

for i in range(JUMLAH_BOMB):
    bom = Bomb()
    semua_sprite.add(bom)
    grup_bomb.add(bom)

for i in range(JUMLAH_COIN):
    koin = Coin()
    semua_sprite.add(koin)
    grup_coin.add(koin)

# Variabel Status Permainan
skor = 0
nyawa = 3
font = pygame.font.SysFont("Arial", 28, bold=True)
game_over = False
berjalan = True
paused = False

# Game Loop Utama
while berjalan:
    # 1. Mengecek event tombol dari pemain
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            berjalan = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                berjalan = False

            if event.key == pygame.K_r and game_over:
                skor = 0
                nyawa = 3
                game_over = False
                player.rect.x = LEBAR // 2

                for bom in grup_bomb:
                    bom.reset_posisi()
                for koin in grup_coin:
                    koin.reset_posisi()

            if event.key == pygame.K_p and not game_over:
                paused = True

            if event.key == pygame.K_RETURN and paused:
                paused = False

    # 2. Update logika HANYA JIKA tidak Game Over DAN tidak sedang di-Pause
    if not game_over and not paused:
        semua_sprite.update()

        tabrakan_coin = pygame.sprite.spritecollide(player, grup_coin, False)
        for c in tabrakan_coin:
            skor += 10
            c.reset_posisi()

        tabrakan_bomb = pygame.sprite.spritecollide(player, grup_bomb, False)
        for b in tabrakan_bomb:
            nyawa -= 1
            b.reset_posisi()
            if nyawa <= 0:
                game_over = True

    # 3. Menggambar ulang layar (Render)
    # --- FITUR BARU: Menggunakan gambar background, bukan lagi Layar.fill(HITAM) ---
    Layar.blit(gambar_background, (0, 0))

    semua_sprite.draw(Layar)

    # Teks HUD (Skor & Nyawa)
    teks_skor = font.render(f"Skor: {skor}", True, PUTIH)
    teks_nyawa = font.render(f"Nyawa: {nyawa}", True, PUTIH)
    Layar.blit(teks_skor, (10, 10))
    Layar.blit(teks_nyawa, (10, 45))

    # Tampilan saat Game Over
    if game_over:
        font_go = pygame.font.SysFont("Arial", 50, bold=True)
        font_opsi = pygame.font.SysFont("Arial", 24, bold=True)

        teks_go = font_go.render("GAME OVER!", True, MERAH_FALLBACK)
        teks_restart = font_opsi.render("Tekan 'R' untuk Main Lagi", True, KUNING_FALLBACK)
        teks_keluar = font_opsi.render("Tekan 'ESC' untuk Keluar", True, PUTIH)

        Layar.blit(teks_go, (LEBAR // 2 - 150, TINGGI // 2 - 60))
        Layar.blit(teks_restart, (LEBAR // 2 - 135, TINGGI // 2 + 10))
        Layar.blit(teks_keluar, (LEBAR // 2 - 130, TINGGI // 2 + 50))

    # Tampilan layar saat di-Pause
    elif paused:
        font_pause = pygame.font.SysFont("Arial", 50, bold=True)
        font_opsi = pygame.font.SysFont("Arial", 24, bold=True)

        teks_pause = font_pause.render("GAME PAUSED", True, KUNING_FALLBACK)
        teks_resume = font_opsi.render("Tekan ENTER untuk lanjut.", True, PUTIH)

        Layar.blit(teks_pause, (LEBAR // 2 - 170, TINGGI // 2 - 50))
        Layar.blit(teks_resume, (LEBAR // 2 - 130, TINGGI // 2 + 20))

    pygame.display.flip()
    Jam.tick(60)

pygame.quit()