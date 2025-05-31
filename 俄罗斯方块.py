import pygame
import random
import os

# 初始化pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I - 青色
    (0, 0, 255),    # J - 蓝色
    (255, 165, 0),  # L - 橙色
    (255, 255, 0),  # O - 黄色
    (0, 255, 0),    # S - 绿色
    (128, 0, 128),  # T - 紫色
    (255, 0, 0)     # Z - 红色
]

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # 更宽的屏幕用于信息面板
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    
    [[1, 0, 0],
     [1, 1, 1]],     # J
     
    [[0, 0, 1],
     [1, 1, 1]],     # L
     
    [[1, 1],
     [1, 1]],        # O
     
    [[0, 1, 1],
     [1, 1, 0]],     # S
     
    [[0, 1, 0],
     [1, 1, 1]],     # T
     
    [[1, 1, 0],
     [0, 1, 1]]      # Z
]

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

clock = pygame.time.Clock()

# 尝试加载中文字体
try:
    # 尝试使用系统字体
    font_path = None
    # Windows 常见中文字体
    if os.name == 'nt':
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simkai.ttf",  # 楷体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
        ]
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
    
    # macOS 常见中文字体
    elif os.name == 'posix':
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # 苹方
            "/System/Library/Fonts/STHeiti Medium.ttc",  # 黑体
        ]
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
    
    # 如果找到字体文件，使用它
    if font_path:
        font_large = pygame.font.Font(font_path, 36)
        font_medium = pygame.font.Font(font_path, 30)
        font_small = pygame.font.Font(font_path, 24)
    else:
        # 如果找不到中文字体，使用默认字体（可能无法显示中文）
        font_large = pygame.font.SysFont(None, 36)
        font_medium = pygame.font.SysFont(None, 30)
        font_small = pygame.font.SysFont(None, 24)
except:
    # 如果所有尝试都失败，使用默认字体
    font_large = pygame.font.SysFont(None, 36)
    font_medium = pygame.font.SysFont(None, 30)
    font_small = pygame.font.SysFont(None, 24)

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # 方块下落速度（秒/格）
        self.fall_time = 0
        
    def new_piece(self):
        # 随机选择一个方块形状和颜色
        shape_idx = random.randint(0, len(SHAPES)-1)
        shape = SHAPES[shape_idx]
        color = COLORS[shape_idx]
        
        # 初始位置（顶部中间）
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {"shape": shape, "color": color, "x": x, "y": y}
    
    def valid_move(self, piece, x_offset=0, y_offset=0):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + x_offset
                    new_y = piece["y"] + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def rotate_piece(self):
        # 旋转当前方块
        piece = self.current_piece
        rotated_shape = [list(row) for row in zip(*piece["shape"][::-1])]
        
        old_shape = piece["shape"]
        piece["shape"] = rotated_shape
        
        # 如果旋转导致碰撞，恢复原状
        if not self.valid_move(piece):
            piece["shape"] = old_shape
    
    def lock_piece(self):
        # 将当前方块固定在网格中
        for y, row in enumerate(self.current_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece["y"] + y][self.current_piece["x"] + x] = self.current_piece["color"]
        
        # 检查是否有完整的行可以消除
        self.clear_lines()
        
        # 获取下一个方块
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # 检查游戏是否结束
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_cleared += 1
                # 将上方的行下移
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1][:]
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
        
        # 更新分数
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += [100, 300, 500, 800][min(lines_cleared-1, 3)] * self.level
        
        # 每消除10行升一级
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def update(self, delta_time):
        if self.game_over or self.paused:
            return
            
        self.fall_time += delta_time
        
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.valid_move(self.current_piece, 0, 1):
                self.current_piece["y"] += 1
            else:
                self.lock_piece()
    
    def draw(self):
        # 绘制游戏区域背景
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(screen, GRAY, (GAME_AREA_LEFT, 0, BLOCK_SIZE * GRID_WIDTH, SCREEN_HEIGHT))
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, BLACK, 
                            (GAME_AREA_LEFT + x * BLOCK_SIZE, 0), 
                            (GAME_AREA_LEFT + x * BLOCK_SIZE, SCREEN_HEIGHT))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, BLACK, 
                            (GAME_AREA_LEFT, y * BLOCK_SIZE), 
                            (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE, y * BLOCK_SIZE))
        
        # 绘制已固定的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                     BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, BLACK, 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                     BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 绘制当前方块
        if not self.game_over:
            for y, row in enumerate(self.current_piece["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_piece["color"], 
                                        (GAME_AREA_LEFT + (self.current_piece["x"] + x) * BLOCK_SIZE, 
                                         (self.current_piece["y"] + y) * BLOCK_SIZE, 
                                         BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(screen, BLACK, 
                                        (GAME_AREA_LEFT + (self.current_piece["x"] + x) * BLOCK_SIZE, 
                                         (self.current_piece["y"] + y) * BLOCK_SIZE, 
                                         BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 绘制下一个方块预览
        info_x = GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 20
        pygame.draw.rect(screen, (70, 70, 70), (info_x - 10, 20, BLOCK_SIZE * 5, BLOCK_SIZE * 5))
        
        next_text = font_medium.render("下一个方块:", True, WHITE)
        screen.blit(next_text, (info_x, 5))
        
        for y, row in enumerate(self.next_piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.next_piece["color"], 
                                   (info_x + x * BLOCK_SIZE, 
                                    40 + y * BLOCK_SIZE, 
                                    BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, BLACK, 
                                   (info_x + x * BLOCK_SIZE, 
                                    40 + y * BLOCK_SIZE, 
                                    BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # 绘制信息面板
        # 绘制分数
        score_text = font_medium.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (info_x, 160))
        
        # 绘制等级
        level_text = font_medium.render(f"等级: {self.level}", True, WHITE)
        screen.blit(level_text, (info_x, 200))
        
        # 绘制消除行数
        lines_text = font_medium.render(f"消除行数: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (info_x, 240))
        
        # 绘制控制说明
        controls_y = 300
        controls = [
            "游戏控制:",
            "←→: 左右移动",
            "↑: 旋转方块",
            "↓: 加速下落",
            "空格: 直接落底",
            "P: 暂停游戏",
            "R: 重新开始"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = font_small.render(text, True, WHITE)
            screen.blit(ctrl_text, (info_x, controls_y + i * 25))
        
        # 游戏暂停提示
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            pause_text = font_large.render("游戏暂停", True, (255, 255, 0))
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            screen.blit(pause_text, text_rect)
            
            continue_text = font_medium.render("按P键继续", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            screen.blit(continue_text, continue_rect)
        
        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font_large.render("游戏结束!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            screen.blit(game_over_text, text_rect)
            
            final_score = font_medium.render(f"最终分数: {self.score}", True, WHITE)
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            screen.blit(final_score, score_rect)
            
            restart_text = font_medium.render("按R键重新开始", True, (0, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
            screen.blit(restart_text, restart_rect)

# 创建游戏实例
game = Tetris()

# 游戏主循环
running = True
last_time = pygame.time.get_ticks()

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0  # 转换为秒
    last_time = current_time
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # 重新开始游戏
            if event.key == pygame.K_r:
                game = Tetris()
            
            # 暂停/继续游戏
            if event.key == pygame.K_p:
                game.paused = not game.paused
            
            if not game.game_over and not game.paused:
                if event.key == pygame.K_LEFT and game.valid_move(game.current_piece, -1, 0):
                    game.current_piece["x"] -= 1
                elif event.key == pygame.K_RIGHT and game.valid_move(game.current_piece, 1, 0):
                    game.current_piece["x"] += 1
                elif event.key == pygame.K_DOWN and game.valid_move(game.current_piece, 0, 1):
                    game.current_piece["y"] += 1
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:  # 硬降落
                    while game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                    game.lock_piece()
    
    # 更新游戏状态
    game.update(delta_time)
    
    # 绘制游戏
    game.draw()
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)

pygame.quit()
