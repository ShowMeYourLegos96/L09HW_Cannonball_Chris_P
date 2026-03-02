from math import sin, cos, radians

import altair as alt
import pandas as pd
import streamlit as st
import random


## Represent a cannonball, tracking its position and velocity.
#
class Cannonball:
    ## Create a new cannonball at the provided x position.
    #  @param x the x position of the ball
    #
    def __init__(self, x): #made the init method into a public method 
        self._x = x
        self._y = 0
        self._vx = 0
        self._vy = 0

    ## Move the cannon ball, using its current velocities.
    #  @param sec the amount of time that has elapsed.
    #
    def move(self, sec, grav):
        dx = self._vx * sec
        dy = self._vy * sec

        self._vy = self._vy - grav * sec

        self._x = self._x + dx
        self._y = self._y + dy

    ## Get the current x position of the ball.
    #  @return the x position of the ball
    #
    def getX(self):
        return self._x

    ## Get the current y position of the ball.
    #  @return the y position of the ball
    #
    def getY(self):
        return self._y

    ## Shoot the canon ball.
    #  @param angle the angle of the cannon (radians)
    #  @param velocity the initial velocity of the ball
    #
    def shoot(self, angle, velocity, user_grav, step=0.1):
        self._vx = velocity * cos(angle)
        self._vy = velocity * sin(angle)
        self.move(step, user_grav)

        #xs = []
        #ys = []

        #while self.getY() > 1e-14:
            #xs.append(self.getX())
            #ys.append(self.getY())
            #self.move(step, user_grav)

        #return xs, ys
    
#created a crazyball class with a modified move method    
class CrazyBall(Cannonball):
  
  def move(self, sec,grav ):
      if self.getX() < 400:
          self.rand_q = random.randrange(0,10)

#creating a Print_IFace class that got a HAS-A relationship with the Cannonball class
class Print_Iface:
    def main_print(self,user_grav,step):
      xs = []
      ys = []

      while self.getY() > 1e-14:
            xs.append(self.getX())
            ys.append(self.getY())
            self.move(step, user_grav)

      return xs, ys

def run_app():
    st.title("Cannonball Trajectory")

    angle_deg = st.number_input(
        "Starting angle (degrees)", min_value=0.0, max_value=90.0, value=45.0
    )
    velocity = st.selectbox("Initial velocity", options=[15, 25, 40], index=1)

    gravity_options = {"Earth": 9.81 , "Moon": 1.62, "Crazy": CrazyBall}
    gravity_name = st.selectbox("Gravity", options=list(gravity_options.keys()), index=0)
    gravity = gravity_options[gravity_name]
    step = .1

    col1, col2 = st.columns(2)
    simulate = col1.button("Simulate")

    if simulate:
        angle_rad = radians(angle_deg)
        ball = Cannonball(0)
        xs, ys = ball.shoot(angle_rad, velocity, gravity, step)

        if not xs:
            st.warning("No trajectory points were generated.")
            return

        df = pd.DataFrame({"x": xs, "y": ys})

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("x:Q", scale=alt.Scale(domain=[0, 200]), title="Distance (m)"),
                y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 100]), title="Height (m)")
            )
            .properties(width=700, height=400)
        )
        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    run_app()
