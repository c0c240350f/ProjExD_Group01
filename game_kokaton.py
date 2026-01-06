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
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
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
        self.hp = 10
        

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
    def __init__(self,):
        """
        左から右に流れる爆弾円Surfaceを生成する
        """
        super().__init__()
        rad = random.randint(15, 25)  # 爆弾円の半径：5以上20以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        self.color = random.randint(1,3)  # ランダムで色を決定する
        if self.color == 1:
            for r in range (rad, 0, -1):
                alpha = int(250*(r/rad))
                pg.draw.circle(self.image, (alpha,0,0), (rad, rad), r)
        if self.color == 2:
            for r in range (rad, 0, -1):
                alpha = int(250*(r/rad))
                pg.draw.circle(self.image, (0,alpha,0), (rad, rad), r)
        if self.color == 3:
            for r in range (rad, 0, -1):
                alpha = int(250*(r/rad))
                pg.draw.circle(self.image, (0,0,alpha), (rad, rad), r)

        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH - 25, random.randint(0,HEIGHT)
        self.vx, self.vy = -3, 0
        self.speed = random.randint(2,3)
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
        self.color = 250
        for r in range (rad, 0, -1):
            alpha = int(self.color*(r/rad))
            pg.draw.circle(self.image, (alpha,0,alpha), (rad, rad), r)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = bomb.rect.center
        self.vx, self.vy = 0, 0

        
        #爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(bomb.rect, bird.rect)
        self.vx -= 0.9  
        if self.vx == 0:
            self.vx = 0.1
        if self.vy == 0:
            self.vy = 0.1
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



class Shot(pg.sprite.Sprite):
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
class Enemy(pg.sprite.Sprite):
    """
    敵に関するクラス
    """
    
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)] #画像読み込み
    
    #def __init__(self):
        #super().__init__()
        #self.image =
        #self.rect = 
        #self.rect.center = 
        #self.vx, self.vy = 
        
    #def update(self):
    def __init__(self):
        """
        画像がランダムな位置で横スクロールする
        """
        super().__init__()

    
        original_image = random.choice(Enemy.imgs) #ランダムな画像の読みこみ
        self.image = pg.transform.rotozoom(original_image, 0, 0.8) #画像の大きさを設定
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(0,50) #x座標の位置をランダムにして調整
        self.rect.y = HEIGHT - random.randint(100, 500) #y座標の位置をランダムにして調整　


        self.base_speed = random.randint(1,6) #スピードを5段階に
        self.speed = self.base_speed
        self.interval = random.randint(50,300)
    def slow_speed(self):
        self.speed = self.base_speed *0.5
    
    
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0: #右の座標が0より小さかったら
            self.rect.x = WIDTH + random.randint(0,50)
            self.rect.y = HEIGHT - random.randint(100, 500)
        



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


class Aim(pg.sprite.Sprite):
    """
    照準機能に関するクラス
    """
    def __init__(self,mouse_pos:tuple[int,int],b_num:int) -> None:
        """
        カーソルの位置を取得する 
        引数１ mouse_pos: カーソルの位置
        引数２ b_num: 残弾数
        """
        self.target_img=pg.image.load("fig/target.png")
        self.target_img=pg.transform.scale(self.target_img,(60,60))
        self.x=mouse_pos[0]
        self.y=mouse_pos[1]
        self.b=b_num
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.image = self.font.render(f"bullets: {self.b}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-100

    def update(self,screen:pg.Surface) -> None:
        """
        カーソルの位置に赤い円を描画する＋残弾数を表示する
        引数１ screen: 画面surface
        """
        screen.blit(self.target_img,[self.x-28,self.y-26])
        screen.blit(self.image,self.rect)
    

class Point:
    """
    爆発用の座標のクラス
    """
    def __init__(self, pos:tuple[int,int]) -> None:
        """
        クリックした座標
        引数１ pos: エフェクトを描画する座標
        """
        self.rect = pg.Rect(0, 0, 0, 0)
        self.rect.center = pos


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
        if total_sec < 30:
            return "D"
        elif total_sec < 60:
            return "C"
        elif total_sec < 120:
            return "B"
        elif total_sec < 180:
            return "A"
        else:
            return "S"

    def update(self, screen: pg.Surface, tmr: int):
        if (tmr // 60) < 30:
            rank = "D"
        elif (tmr // 60) < 60:
            rank = "C"
        elif (tmr // 60) < 120:
            rank = "B"
        elif (tmr // 60) < 180:
            rank = "A"
        else:
            rank = "S"

        self.image = self.font.render(f"Rank:{rank}", 0, self.color)
        screen.blit(self.image, self.rect)

        
class HP:
    """
    体力を表示するクラス
    """
    def __init__(self, bird: Bird):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = bird.hp  # こうかとんのHP
        self.image = self.font.render(f"HP: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH/2, 30

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"HP: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)



class Item(pg.sprite.Sprite):
    """
    アイテムに関連するクラス
    """
    def __init__(self,hp):
        super().__init__()
        self.num = random.randint(0,2)  # ランダムで画像を設定するための乱数
        self.item = pg.image.load(f"fig/item{self.num}.png")  # 乱数の値によって画像を変える
        self.image = pg.transform.rotozoom(self.item, random.randint(0,360), 0.25)  # ランダムな角度を設定
        self.rect = self.image.get_rect()
        self.rect.center =  WIDTH, random.randint(0, HEIGHT)  # 画面右側のランダムな高さから出現
        self.vx, self.vy = random.randint(-10,-5),0  # ランダムな速度で左に流れる
        self.count = 0  
        self.hp = hp

    def get_item(self):
        """
        アイテムを獲得したときのメソッド
        アイテムを削除する
        """
        self.kill()
        return

        # for i in range(3):  # アイテムの個数分繰り返し
        #     if self.num != i:  # iが画像番号でないときは処理を行わない
        #         continue
        #     else: 
        #         self.kill()  # 削除
        #         if i == 0:  # 画像番号ごとに効果を付ける
        #             self.count += 1
        #             self.hp.value += 3
        #             # 回復
        #         elif i == 1:
        #             self.count += 5
        #             # 重力場
        #         elif i == 2:
        #             self.count += 10
        #             # 無敵

        # return self.count

    def update(self):
        self.rect.move_ip(self.vx, self.vy)    

class Click(pg.sprite.Sprite):
    
    def __init__(self,aim):
        super().__init__
        self.life = 5
        

        

def main():
    pg.display.set_caption("シューティングゲーム")
    screen = pg.display.set_mode((WIDTH,HEIGHT))
    bg_img = pg.image.load(f"fig/bg_moon_getsumen.jpg")
    bg_img = pg.transform.scale(bg_img, (1600,900))
    bg_img2 = pg.transform.flip(bg_img,True,False)  # 横スクロール用の反転画像
    score = Score()

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    minbombs = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravitys = pg.sprite.Group()
    shots = pg.sprite.Group()
    count = Time()
    rank = Rank()

    items = pg.sprite.Group()
    hp = HP(bird)

    mouse_pos=pg.mouse.get_pos()
    
    tmr = 0
    slow_timer = 0
    clock = pg.time.Clock()

    
    last_explosion_time = -100
    EXP_COOLTIME = 15
    rl=10
    last_reload_time = 0
    RELOAD_INTERVAL = 200
    aim=Aim(pg.mouse.get_pos(),rl)

    while True:
        key_lst = pg.key.get_pressed()
        mouse_pos=pg.mouse.get_pos()
        
        aim=Aim(mouse_pos,rl)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird.speed = 20
                
            else:
                bird.speed = 10
            
            if event.type==pg.MOUSEBUTTONDOWN: #マウスがクリックされたら
                if tmr-last_explosion_time >= EXP_COOLTIME: #クールタイム確認
                    if rl >= 1:
                        p = Point(pg.mouse.get_pos())
                        shots.add(Shot(p, 10))
                        last_explosion_time = tmr
                        rl -= 1

        if tmr - last_reload_time >= RELOAD_INTERVAL and rl < 10:
            rl += 1
            last_reload_time = tmr 

        x = tmr % 3200  # xを0から3199の範囲で変化させる
        screen.blit(bg_img, [-x, 0])  # 最初の背景画像（画面左端からスクロール量 -x の位置）
        screen.blit(bg_img2, [-x + 1600 ,0])  # 2枚目の背景画像（1枚目の右端から開始）
        screen.blit(bg_img, [-x + 3200, 0])  # 3枚目の背景画像（2枚目の右端から開始）
        
        gravitys.update()
        gravitys.draw(screen)
        if tmr < 250:
            spawn_interval = 300  # 300フレームごとに敵出現
        elif tmr < 750:
            spawn_interval = 200  # 200フレームごとに敵出現
        else:
            spawn_interval = 150  # 150フレームごとに敵出現
        if tmr % spawn_interval == 0:
            emys.add(Enemy())
        for emy in emys:
            if  tmr%emy.interval == 0:
                    #intervalに応じて爆弾投下
                    minbombs.add(Minbomb(emy, bird))
        

        if tmr >= 250 and tmr%50 == 0:  # 一定時間経過後に50フレームに1回，爆弾を出現させる
            bombs.add(Bomb())
        elif tmr >= 500 and tmr%25 == 0:  # 一定時間経過後に25フレームに1回，爆弾を出現させる
            bombs.add(Bomb())
        elif tmr >= 1500 and tmr%10 == 0:  # 一定時間経過後に25フレームに1回，爆弾を出現させる
            bombs.add(Bomb())
        if tmr >= 1000:
            for bomb in bombs: #大きい爆弾から,追従する小さい爆弾を出現させる
                if  tmr%bomb.interval == 0:
                    #intervalに応じて爆弾投下
                    minbombs.add(Minbomb(bomb, bird))
        if tmr >= 1500:
            for bomb in bombs: #大きい爆弾から,追従する小さい爆弾を出現させる
                if  tmr%bomb.interval == 100:
                    #intervalに応じて爆弾投下
                    minbombs.add(Minbomb(bomb, bird))
                    
        # if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
        #     emys.add(Enemy())

        # for emy in emys:
        #     if emy.state == "stop" and tmr%emy.interval == 0:
        #         # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
        #         bombs.add(Bomb(emy, bird))

        if tmr%250 == 0:  # 100フレームに1回，アイテムを出現させる
            items.add(Item(hp))

        if slow_timer != 0:
            slow_timer -= 1
            if len(emys) != 0:
                for emy in emys:
                    emy.slow_speed()


        for emy in pg.sprite.groupcollide(emys, shots , True, False).keys():  # ビームと衝突した敵機リスト
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ


        for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
            # if bird.state != "hyper":  # 無敵状態でないならゲームオーバー
            #     if bomb.state=="active":
            # if bomb.state=="active":
                if hp.value <= 1:  # HPが1以下ならゲームオーバー
                    bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                    score.update(screen)
                    # result = tmr // 60
                    # print(result)

                    gameover(screen, rank.get_rank(tmr))
                    pg.display.update()
                    time.sleep(2)
                    return
                else:  # HPが1より大きければHPが1減る
                    hp.value -= 1
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.value += 1  # 1点アップ
                #exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        for minbomb in pg.sprite.spritecollide(bird, minbombs, True):  # こうかとんと衝突した爆弾リスト
            # if bird.state != "hyper":  # 無敵状態でないならゲームオーバー
            #     if bomb.state=="active":
            if hp.value <= 1:  # HPが1以下ならゲームオーバー
                bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                score.update(screen)
                gameover(screen, rank.get_rank(tmr))
                pg.display.update()
                time.sleep(2)
                return
            else:  # HPが1より大きければHPが1減る
                hp.value -= 1
            exps.add(Explosion(minbomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
        
           
        # if len(gravitys)>0:
        #     for emy in emys:
        #         exps.add(Explosion(emy,50))  # 爆発エフェクト
        #         emy.kill()
        #     for bomb in bombs:
        #         exps.add(Explosion(bomb, 50))  # 爆発エフェクト
        #         bomb.kill()
                #exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        for bomb in pg.sprite.groupcollide(bombs, shots, True,False):#照準の接触判定
            exps.add(Explosion(bomb,50))  # 爆発エフェクト
            bomb.kill()
        for minbomb in pg.sprite.groupcollide(minbombs, shots, True,False):#照準の接触判定
            exps.add(Explosion(minbomb, 50))  # 爆発エフェクト
            minbomb.kill()

        # if len(gravitys)>0:
        #     for emy in emys:
        #         exps.add(Explosion(emy,50))  # 爆発エフェクト
        #         emy.kill()
        #     for bomb in bombs:
        #         exps.add(Explosion(bomb, 50))  # 爆発エフェクト
        #         bomb.kill()
        #         else:  # HPが1より大きければHPが1減る
        #             hp.value -= 1
        #     exps.add(Explosion(bomb, 50))  # 爆発エフェクト
        #     score.value += 1  # 1点アップ

        #for item in pg.sprite.spritecollide(bird, items, True): # アイテムとの衝突判定
        for item in pg.sprite.groupcollide(items, shots, True,False): # アイテムとの衝突判定
            if item.num == 0:  # 0番のアイテム(キャンディ)を取るとHPが1回復
                if hp.value < 10:
                    hp.value += 1 
            elif item.num == 1:  # 1番のアイテム(ストロベリー)を取ると画面上の敵を倒す
                gravitys.add(Gravity(50))
                if len(emys) != 0:
                    for emy in emys:
                        exps.add(Explosion(emy,50))  # 爆発エフェクト
                        emy.kill()
                if len(bombs) != 0:
                    for bomb in bombs:
                        exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                        bomb.kill()
                if len(minbombs) != 0:
                    for minbomb in minbombs:
                        minbomb.kill()
            elif item.num == 2:  # 画面上の敵の減速
                slow_timer = 200
                rl += 5
                # if len(emys) != 0:
                #     for emy in emys:
                #         emy.slow_speed()
            else:  # 必要に応じて追加
                pass
            item.get_item()

    
        # if len(gravitys)>0:
        #     for emy in emys:
        #         exps.add(Explosion(emy,50))  # 爆発エフェクト
        #         emy.kill()
        #     for bomb in bombs:
        #         exps.add(Explosion(bomb, 50))  # 爆発エフェクト
        #         bomb.kill()

            
        

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
        count.update(screen, tmr)
        rank.update(screen,tmr)
        shots.update()
        shots.draw(screen)
        hp.update(screen)
        items.update()
        items.draw(screen)
        aim.update(screen)
        
        pg.display.update()
        tmr += 1
        clock.tick(60)
        


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()