import turtle
import random
import time
import platform

def main():
    # Setup screen
    wn = turtle.Screen()
    wn.title("Pong by Maalek Darkal")
    wn.bgcolor("black")
    wn.setup(width=900, height=700)
    wn.tracer(0)

    # --- MENU STATE ---
    mode = None
    difficulty_name = None
    ai_enabled = False
    ai_speed = 12

    # Draw menu
    title = turtle.Turtle()
    title.color("white")
    title.penup()
    title.hideturtle()
    title.goto(0, 200)
    title.write("PONG", align="center", font=("Courier", 48, "bold"))

    menu = turtle.Turtle()
    menu.color("yellow")
    menu.penup()
    menu.hideturtle()
    menu.goto(0, 50)
    menu.write("Press '1' for Single Player\nPress '2' for Multiplayer",
                align="center", font=("Courier", 24, "normal"))

    # Mode select handlers
    def set_single():
        nonlocal mode, ai_enabled
        mode = "single"
        ai_enabled = True
        show_difficulty_menu()

    def set_multi():
        nonlocal mode, ai_enabled
        mode = "multi"
        ai_enabled = False
        start_game()

    # Listen for menu input
    wn.listen()
    wn.onkeypress(set_single, "1")
    wn.onkeypress(set_multi, "2")

    # --- Difficulty selection ---
    def show_difficulty_menu():
        title.clear()
        menu.clear()
        title.write("Select Difficulty", align="center", font=("Courier", 36, "bold"))
        menu.write("1. Easy\n2. Medium\n3. Hard\n4. Impossible",
                    align="center", font=("Courier", 24, "normal"))

        def easy(): start_game("Easy")
        def medium(): start_game("Medium")
        def hard(): start_game("Hard")
        def impossible(): start_game("Impossible")

        wn.onkeypress(easy, "1")
        wn.onkeypress(medium, "2")
        wn.onkeypress(hard, "3")
        wn.onkeypress(impossible, "4")

    # --- Start actual game ---
    def start_game(difficulty="Medium"):
        nonlocal ai_enabled, difficulty_name, ai_speed
        difficulty_name = difficulty
        title.clear()
        menu.clear()

        # Difficulty settings
        if ai_enabled:
            if difficulty == "Easy":
                ai_speed = 10
            elif difficulty == "Medium":
                ai_speed = 11
            elif difficulty == "Hard":
                ai_speed = 13
            elif difficulty == "Impossible":
                ai_speed = 14

        # Scores
        score_a = 0
        score_b = 0

        # Paddle settings
        PADDLE_MOVE = 30
        PADDLE_LIMIT = 260

        # Paddle A (left)
        paddle_a = turtle.Turtle()
        paddle_a.speed(0)
        paddle_a.shape("square")
        paddle_a.color("blue")
        paddle_a.shapesize(stretch_wid=5, stretch_len=1)
        paddle_a.penup()
        paddle_a.goto(-350, 0)

        # Paddle B (right)
        paddle_b = turtle.Turtle()
        paddle_b.speed(0)
        paddle_b.shape("square")
        paddle_b.color("red")
        paddle_b.shapesize(stretch_wid=5, stretch_len=1)
        paddle_b.penup()
        paddle_b.goto(350, 0)

        # Ball
        ball = turtle.Turtle()
        ball.speed(0)
        ball.shape("circle")
        ball.color("grey")
        ball.penup()
        ball.goto(0, 0)
        INIT_SPEED = 4.0
        ball.dx = INIT_SPEED * random.choice([-1, 1])
        ball.dy = INIT_SPEED * random.choice([-1, 1])

        # 🎨 Color list for color-changing ball
        ball_colors = ["white", "cyan", "magenta", "orange", "lime", "violet", "yellow"]
        color_change_counter = 0  # counts paddle hits

        # Scoreboard
        pen = turtle.Turtle()
        pen.speed(0)
        pen.color("green")
        pen.penup()
        pen.hideturtle()
        pen.goto(0, 300)
        pen.write("Player A: 0  Player B: 0", align="center", font=("Courier", 24, "normal"))

        info = turtle.Turtle()
        info.speed(0)
        info.color("yellow")
        info.penup()
        info.hideturtle()
        info.goto(0, 270)
        info.write("First to 10 wins!", align="center", font=("Courier", 18, "normal"))

        # Movement
        def paddle_a_up():
            y = paddle_a.ycor()
            if y < PADDLE_LIMIT:
                paddle_a.sety(y + PADDLE_MOVE)

        def paddle_a_down():
            y = paddle_a.ycor()
            if y > -PADDLE_LIMIT:
                paddle_a.sety(y - PADDLE_MOVE)

        def paddle_b_up():
            if not ai_enabled:
                y = paddle_b.ycor()
                if y < PADDLE_LIMIT:
                    paddle_b.sety(y + PADDLE_MOVE)

        def paddle_b_down():
            if not ai_enabled:
                y = paddle_b.ycor()
                if y > -PADDLE_LIMIT:
                    paddle_b.sety(y - PADDLE_MOVE)

        wn.listen()
        wn.onkeypress(paddle_a_up, "w")
        wn.onkeypress(paddle_a_down, "s")
        wn.onkeypress(paddle_b_up, "Up")
        wn.onkeypress(paddle_b_down, "Down")

        # Normalize speed helper
        def normalize_speed():
            max_speed = 16
            if abs(ball.dx) > max_speed:
                ball.dx = max_speed * (1 if ball.dx > 0 else -1)
            if abs(ball.dy) > max_speed:
                ball.dy = max_speed * (1 if ball.dy > 0 else -1)

        # --- Countdown before start ---
        def show_countdown():
            countdown_pen = turtle.Turtle()
            countdown_pen.hideturtle()
            countdown_pen.color("yellow")
            countdown_pen.penup()
            countdown_pen.goto(0, 0)
            for num in ["3", "2", "1", "GO!"]:
                countdown_pen.clear()
                countdown_pen.write(num, align="center", font=("Courier", 48, "bold"))
                wn.update()
                time.sleep(0.7)
            countdown_pen.clear()

        # --- Show Play Again Screen ---
        def show_play_again():
            pen.clear()
            info.clear()
            pen.goto(0, 50)
            pen.color("yellow")
            pen.write("Press 'R' to Play Again\nPress 'Q' to Main Menu",
                      align="center", font=("Courier", 24, "normal"))

            def restart():
                pen.clear()
                info.clear()
                start_game(difficulty_name)  # restart current game

            def back_to_menu():
                pen.clear()
                info.clear()
                wn.clear()
                main()  # go back to main menu

            wn.onkeypress(restart, "r")
            wn.onkeypress(back_to_menu, "q")
            wn.listen()

        # 🎬 Start countdown
        show_countdown()

        # Game loop
        while True:
            wn.update()

            # Move ball
            ball.setx(ball.xcor() + ball.dx)
            ball.sety(ball.ycor() + ball.dy)

            # Top / bottom bounce
            if ball.ycor() > 340:
                ball.sety(340)
                ball.dy *= -1
            if ball.ycor() < -340:
                ball.sety(-340)
                ball.dy *= -1

            # Right wall (A scores)
            if ball.xcor() > 440:
                score_a += 1
                pen.clear()
                pen.write(f"Player A: {score_a}  Player B: {score_b}", align="center", font=("Courier", 24, "normal"))
                ball.goto(0, 0)
                ball.dx = -INIT_SPEED
                ball.dy = INIT_SPEED * random.choice([-1, 1])
                show_countdown()
                time.sleep(0.4)

            # Left wall (B scores)
            if ball.xcor() < -440:
                score_b += 1
                pen.clear()
                pen.write(f"Player A: {score_a}  Player B: {score_b}", align="center", font=("Courier", 24, "normal"))
                ball.goto(0, 0)
                ball.dx = INIT_SPEED
                ball.dy = INIT_SPEED * random.choice([-1, 1])
                show_countdown()
                time.sleep(0.4)

            # --- Smarter AI movement ---
            if ai_enabled:
                if not hasattr(main, "ai_timer"):
                    main.ai_timer = 0
                main.ai_timer += 1

                reaction_delay = {
                    "Easy": 4,
                    "Medium": 3,
                    "Hard": 3,
                    "Impossible": 1
                }[difficulty_name]

                if main.ai_timer >= reaction_delay:
                    main.ai_timer = 0
                    error_margin = {
                        "Easy": 10,
                        "Medium": 8,
                        "Hard": 7,
                        "Impossible": 2
                    }[difficulty_name]

                    adjusted_speed = ai_speed * (0.8 if abs(ball.dx) > 10 else 1.0)

                    if ball.dx > 0:
                        target_y = ball.ycor() + random.randint(-error_margin, error_margin)
                        if paddle_b.ycor() < target_y - 10:
                            paddle_b.sety(paddle_b.ycor() + adjusted_speed)
                        elif paddle_b.ycor() > target_y + 10:
                            paddle_b.sety(paddle_b.ycor() - adjusted_speed)
                    else:
                        if paddle_b.ycor() > 0:
                            paddle_b.sety(paddle_b.ycor() - adjusted_speed / 2)
                        elif paddle_b.ycor() < 0:
                            paddle_b.sety(paddle_b.ycor() + adjusted_speed / 2)

            # Paddle collisions (wider zone)
            if (310 < ball.xcor() < 370) and (paddle_b.ycor() - 70 < ball.ycor() < paddle_b.ycor() + 70):
                ball.setx(310)
                offset = ball.ycor() - paddle_b.ycor()
                ball.dy = offset / 8
                ball.dx *= -1.05
                ball.dy *= 1.05
                normalize_speed()

                # 🌈 Change ball color on paddle hit
                color_change_counter += 1
                if color_change_counter % 3 == 0:
                    ball.color(random.choice(ball_colors))

            if (-370 < ball.xcor() < -310) and (paddle_a.ycor() - 70 < ball.ycor() < paddle_a.ycor() + 70):
                ball.setx(-310)
                offset = ball.ycor() - paddle_a.ycor()
                ball.dy = offset / 8
                ball.dx *= -1.05
                ball.dy *= 1.05
                normalize_speed()

                # 🌈 Change ball color on paddle hit
                color_change_counter += 1
                if color_change_counter % 3 == 0:
                    ball.color(random.choice(ball_colors))

            # Check winner
            if score_a >= 10:
                pen.clear()
                info.clear()
                pen.goto(0, 0)
                pen.color("yellow")
                pen.write("PLAYER A WINS!", align="center", font=("Courier", 36, "bold"))
                wn.update()
                time.sleep(2)
                show_play_again()
                return

            if score_b >= 10:
                pen.clear()
                info.clear()
                pen.goto(0, 0)
                pen.color("yellow")
                pen.write("PLAYER B WINS!", align="center", font=("Courier", 36, "bold"))
                wn.update()
                time.sleep(2)
                show_play_again()
                return

            # Keep physics stable
            time.sleep(0.01)

    wn.mainloop()

if __name__ == "__main__":
    main()
# End of pong.py
