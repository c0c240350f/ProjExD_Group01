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
    def __init__(self,  bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(15, 25)  # 爆弾円の半径：5以上20以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        for r in range (rad, 0, -1):
            alpha = int(250*(r/rad))
            pg.draw.circle(self.image, (alpha,0,0), (rad, rad), r)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH - 25, random.randint(0,HEIGHT)
        self.vx, self.vy = -3, 0
        self.speed = random.randint(2,4)
        self.interval = random.randint(50,300)
        

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        self.rect
        if check_bound(self.rect) != (True, True):
            self.kill()

class Minbomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    def __init__(self, bomb:Bomb,  bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = 5  # 爆弾円の半径：5
        self.image = pg.Surface((2*rad, 2*rad))
        for r in range (rad, 0, -1):
            alpha = int(250*(r/rad))
            pg.draw.circle(self.image, (alpha,0,alpha), (rad, rad), r)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = bomb.rect.center
        self.vx, self.vy = +1, 0

        
        #爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(bomb.rect, bird.rect)  
        self.rect.centerx = bomb.rect.centerx
        self.rect.centery = bomb.rect.centery+bomb.rect.height//2
        self.speed = random.randint(2,3)
        

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        self.rect
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

def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    score = Score()

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    minbombs = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravitys = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird.speed = 20
            else:
                bird.speed = 10

                
        screen.blit(bg_img, [0, 0])
        gravitys.update()
        gravitys.draw(screen)

        if tmr >= 250 and tmr%50 == 0:  # 一定時間経過後に50フレームに1回，爆弾を出現させる
            bombs.add(Bomb(bird))
        elif tmr >= 500 and tmr%25 == 0:  # 一定時間経過後に25フレームに1回，爆弾を出現させる
            bombs.add(Bomb(bird))

        for bomb in bombs:
            if  tmr%bomb.interval == 0:
                #intervalに応じて爆弾投下
                minbombs.add(Minbomb(bomb, bird))

        #for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():  # ビームと衝突した敵機リスト
            #exps.add(Explosion(emy, 100))  # 爆発エフェクト
            #score.value += 10  # 10点アップ
            #bird.change_img(6, screen)  # こうかとん喜びエフェクト


        for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
            # if bird.state != "hyper":  # 無敵状態でないならゲームオーバー
            #     if bomb.state=="active":
                    bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                    score.update(screen)
                    pg.display.update()
                    time.sleep(2)
                    return
                #exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        for minbomb in pg.sprite.spritecollide(bird, minbombs, True):  # こうかとんと衝突した爆弾リスト
            # if bird.state != "hyper":  # 無敵状態でないならゲームオーバー
            #     if bomb.state=="active":
                    bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                    score.update(screen)
                    pg.display.update()
                    time.sleep(2)
                    return
                #exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        # for bomb in pg.sprite.spritecollide(, bomb, True):#照準の接触判定
        #     exps.add(Explosion(bomb,50))  # 爆発エフェクト
        #     bomb.kill()
        # for minbomb in pg.sprite.spritecollide(, minbombs, True):#照準の接触判定
        #     exps.add(Explosion(minbomb, 50))  # 爆発エフェクト
        #     minbomb.kill()

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
        minbombs.update()
        minbombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)
        


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
