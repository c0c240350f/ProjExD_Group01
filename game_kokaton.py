import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


def gameover(screen: pg.Surface, res_rank: str) -> None:
    """
    引数：screen
    戻り値：なし
    ゲームオーバー画面を表示する
    """
    gameover_img = pg.Surface((1100,650))
    pg.draw.rect(gameover_img, (0,0,0), (0,0,WIDTH,HEIGHT))
    gameover_img.set_alpha(200)
    fonto = pg.font.Font(None,80)
    txt = fonto.render("Game Over", True, (255,255,255))
    gameover_img.blit(txt, [400,300])
    rank_font = pg.font.Font(None, 60)
    rank_txt = rank_font.render(f"Rank: {res_rank}", True, (255,255,255))
    gameover_img.blit(rank_txt, [470,400])
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 350,325
    gameover_img.blit(kk_img,kk_rct)
    kk2_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk2_rct = kk2_img.get_rect()
    kk2_rct.center = 750,325
    gameover_img.blit(kk2_img,kk2_rct)
    screen.blit(gameover_img, [0,0])
    pg.display.update()
    time.sleep(5)


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6
        self.state="active"

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


#class Enemy(pg.sprite.Sprite):
    
    
    #def __init__(self):
        #super().__init__()
        #self.image =
        #self.rect = 
        #self.rect.center = 
        #self.vx, self.vy = 
        
    #def update(self):
        



class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class Gravity(pg.sprite.Sprite):
    """
    重力場に関するクラス
    """
    def __init__(self, life:int):
        super().__init__()
        self.image = pg.Surface((WIDTH, HEIGHT))
        pg.draw.rect(self.image, (0,0,0), self.image.get_rect())
        self.image.set_alpha(150)
        self.rect = self.image.get_rect()
        self.life = life
    
    def update(self):
        """
        重力場の発動時間を1ずつ減算していき、0未満になったら消す
        """
        self.life -= 1
        if self.life < 0:
            self.kill()


class Time():
    """
    タイムをカウントするクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (150, 150, 255)
        self.rect = self.font.render("Time: 00:00", 0, self.color).get_rect()
        self.rect.center = 105, 40
    
    def update(self, screen: pg.Surface, tmr: int):
        total = tmr // 60
        min = total // 60
        sec = total % 60
        time_str = f"Time:{min:02}:{sec:02}"
        self.image = self.font.render(time_str, 0, self.color)
        screen.blit(self.image, self.rect)


class Rank():
    """
    ランクの表示をするクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (150,150,255)
        self.rect = self.font.render("Rank:X", 0, self.color).get_rect()
        self.rect.center = 70, 80

    def get_rank(self, tmr: int) -> str:
        total_sec = tmr // 60
        if total_sec < 15:
            return "D"
        elif total_sec < 45:
            return "C"
        elif total_sec < 75:
            return "B"
        elif total_sec < 105:
            return "A"
        else:
            return "S"

    def update(self, screen: pg.Surface, tmr: int):
        if (tmr // 60) < 15:
            rank = "D"
        elif (tmr // 60) < 45:
            rank = "C"
        elif (tmr // 60) < 75:
            rank = "B"
        elif (tmr // 60) < 105:
            rank = "A"
        else:
            rank = "S"

        self.image = self.font.render(f"Rank:{rank}", 0, self.color)
        screen.blit(self.image, self.rect)

        
        


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH,HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img,True,False)  # 横スクロール用の反転画像
    score = Score()

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravitys = pg.sprite.Group()
    time = Time()
    rank = Rank()
    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird.speed = 20
                return
            else:
                bird.speed = 10

        x = tmr % 3200  # xを0から3199の範囲で変化させる
        screen.blit(bg_img, [-x, 0])  # 最初の背景画像（画面左端からスクロール量 -x の位置）
        screen.blit(bg_img2, [-x + 1600 ,0])  # 2枚目の背景画像（1枚目の右端から開始）
        screen.blit(bg_img, [-x + 3200, 0])  # 3枚目の背景画像（2枚目の右端から開始）
        gravitys.update()
        gravitys.draw(screen)

        #if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            #emys.add(Enemy())

        #for emy in emys:
            #if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                #bombs.add(Bomb(emy, bird))

        #for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():  # ビームと衝突した敵機リスト
            #exps.add(Explosion(emy, 100))  # 爆発エフェクト
            #score.value += 10  # 10点アップ
            #bird.change_img(6, screen)  # こうかとん喜びエフェクト


        for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
            if bird.state != "hyper":  # 無敵状態でないならゲームオーバー
                if bomb.state=="active":
                    bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                    score.update(screen)
                    # result = tmr // 60
                    # print(result)
                    pg.display.update()
                    time.sleep(2)
                    return
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
    
        if len(gravitys)>0:
            for emy in emys:
                exps.add(Explosion(emy,50))  # 爆発エフェクト
                emy.kill()
            for bomb in bombs:
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                bomb.kill()

            
        

        bird.update(key_lst, screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        time.update(screen, tmr)
        rank.update(screen,tmr)

        pg.display.update()
        tmr += 1
        clock.tick(60)
        


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
