import flet as ft
import random
import time
import threading

def main(page: ft.Page):
    # --- 1. 页面基础设置 ---
    page.title = "猜数字大挑战"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 380
    page.window_height = 700

    # --- 2. 全局游戏变量 ---
    game_data = {
        "target": 0,
        "max_num": 100,
        "max_tries": None, 
        "current_tries": 0
    }

    # ================= 界面组件 =================

    txt_hint = ft.Text("请选择游戏难度", size=24, weight=ft.FontWeight.BOLD)
    txt_feedback = ft.Text("", size=18, color=ft.Colors.BLUE) 
    txt_limit = ft.Text("", size=14, color=ft.Colors.RED)

    input_guess = ft.TextField(
        label="输入数字", 
        width=200, 
        text_align=ft.TextAlign.CENTER, 
        keyboard_type=ft.KeyboardType.NUMBER,
        on_submit=lambda e: check_guess(e)
    )

    # ================= 逻辑处理 =================

    def start_game(difficulty):
        game_data["current_tries"] = 0
        
        if difficulty == "easy":
            game_data["max_num"] = 100
            game_data["max_tries"] = None
            txt_limit.value = "模式：无限次数"
        elif difficulty == "medium":
            game_data["max_num"] = 1000
            game_data["max_tries"] = 20
            txt_limit.value = "剩余次数：20"
        else: # hard
            game_data["max_num"] = 1000
            game_data["max_tries"] = 10
            txt_limit.value = "剩余次数：10"
            
        game_data["target"] = random.randint(1, game_data["max_num"])
        print(f"作弊：目标是 {game_data['target']}") 
        
        input_guess.label = f"1 - {game_data['max_num']}"
        input_guess.value = ""
        txt_feedback.value = "准备好了吗？"
        show_game_view()

    def check_guess(e=None):
        if not input_guess.value:
            return
        
        try:
            val = int(input_guess.value)
        except ValueError:
            input_guess.error_text = "请输入纯数字"
            page.update()
            return

        input_guess.error_text = None
        game_data["current_tries"] += 1
        
        print(f"用户猜测: {val}, 目标: {game_data['target']}") 

        # 1. 猜对了
        if val == game_data["target"]:
            handle_win()
            return 
            
        # 2. 猜错了 - 检查次数
        if game_data["max_tries"] is not None:
            remaining = game_data["max_tries"] - game_data["current_tries"]
            txt_limit.value = f"剩余次数：{remaining}"
            if remaining <= 0:
                handle_lose()
                return

        # 3. 给出提示
        if val > game_data["target"]:
            txt_feedback.value = "太大了！⬇️ 往下猜"
            txt_feedback.color = ft.Colors.ORANGE
        else:
            txt_feedback.value = "太小了！⬆️ 往上猜"
            txt_feedback.color = ft.Colors.BLUE
        
        input_guess.value = ""
        input_guess.focus()
        page.update()

    def calculate_score():
        base = 100
        if game_data["max_tries"] is None:
            return max(60, base - (game_data["current_tries"] - 1) * 2)
        else:
            remaining = game_data["max_tries"] - game_data["current_tries"] + 1
            return int((remaining / game_data["max_tries"]) * 100)

    def handle_win():
        score = calculate_score()
        dlg = ft.AlertDialog(
            title=ft.Text("🎉 你真棒！"),
            content=ft.Text(f"答案是 {game_data['target']}\n本次得分：{score} 分\n尝试次数：{game_data['current_tries']}"),
            actions=[
                ft.TextButton("返回菜单", on_click=lambda e: back_to_menu(dlg))
            ],
            modal=True,
        )
        page.open(dlg)

    def handle_lose():
        dlg = ft.AlertDialog(
            title=ft.Text("😞 挑战失败"),
            content=ft.Text(f"机会用光了...\n正确答案是 {game_data['target']}"),
            actions=[
                ft.TextButton("不服再来", on_click=lambda e: back_to_menu(dlg))
            ],
            modal=True,
        )
        page.open(dlg)

    # --- 【关键修复点】 ---
    def back_to_menu(dlg):
        # 1. 关闭弹窗
        page.close(dlg)
        # 2. 提交更新，让关闭动作生效
        page.update()
        # 3. 【核心修复】暂停 0.1 秒
        # 这能防止 "弹窗还没关完，页面就被清空" 导致的卡死
        time.sleep(0.1) 
        # 4. 载入菜单
        show_menu_view()

    # ================= 视图切换 =================

    def show_splash_screen():
        page.clean()
        page.bgcolor = ft.Colors.BLUE
        page.add(
            ft.Column(
                [
                    ft.Icon(name=ft.Icons.QUESTION_MARK, size=100, color=ft.Colors.WHITE),
                    ft.Text("猜数字 Pro", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.ProgressRing(color=ft.Colors.WHITE),
                    ft.Text("加载资源中...", color=ft.Colors.WHITE70)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        def to_menu():
            time.sleep(2)
            show_menu_view()
        threading.Thread(target=to_menu, daemon=True).start()

    def show_menu_view():
        page.clean()
        page.bgcolor = ft.Colors.WHITE
        btn_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=15)
        
        page.add(
            ft.Column(
                [
                    ft.Icon(ft.Icons.GAMES, size=80, color=ft.Colors.BLUE),
                    ft.Text("请选择难度", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    ft.ElevatedButton("简单 (1-100 不限)", on_click=lambda e: start_game("easy"), width=250, style=btn_style, bgcolor=ft.Colors.GREEN),
                    ft.Container(height=10),
                    ft.ElevatedButton("中等 (1-1000 20次)", on_click=lambda e: start_game("medium"), width=250, style=btn_style, bgcolor=ft.Colors.ORANGE),
                    ft.Container(height=10),
                    ft.ElevatedButton("困难 (1-1000 10次)", on_click=lambda e: start_game("hard"), width=250, style=btn_style, bgcolor=ft.Colors.RED),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    def show_game_view():
        page.clean()
        page.bgcolor = ft.Colors.WHITE
        page.add(
            ft.Column(
                [
                    ft.Row([
                        # 这里的返回也统一逻辑，确保安全
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_menu_view()),
                        txt_limit
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Container(height=40),
                    ft.Text("猜猜我是多少？", size=20),
                    input_guess,
                    ft.ElevatedButton("确认提交", on_click=check_guess, width=150, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                    ft.Container(height=20),
                    txt_feedback
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    show_splash_screen()

ft.app(target=main)