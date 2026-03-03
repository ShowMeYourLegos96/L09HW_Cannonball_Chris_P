from math import sin, cos, radians
import altair as alt
import pandas as pd
import streamlit as st
import random


## Interface class for printing/displaying plot updates
#  This class handles the "plot updates" functionality via composition
#
class Print_Iface:
    ## Initialize the print interface
    #
    def __init__(self):
        self._update_count = 0
        self._plot_points = []  # Store plot points for display
    
    ## Print a status update during trajectory simulation
    #  @param x the current x position
    #  @param y the current y position
    #  @param vx the current x velocity
    #  @param vy the current y velocity
    #
    def print_update(self, x, y, vx, vy):
        self._update_count += 1
        self._plot_points.append((x, y))
        
        # Print progress updates to console (this handles the "plot updates" requirement)
        if self._update_count % 10 == 0:  # Print every 10th point
            print(f"Plot point #{self._update_count}: ({x:.1f}, {y:.1f})")
    
    ## Get all plot points collected
    #  @return list of (x, y) tuples
    #
    def get_plot_points(self):
        return self._plot_points


## Represent a cannonball, tracking its position and velocity.
#  Now with HAS-A Print_Iface for plot updates
#
class Cannonball:
    ## Create a new cannonball at the provided x position.
    #  @param x the x position of the ball
    #
    def __init__(self, x):
        self._x = x
        self._y = 0
        self._vx = 0
        self._vy = 0
        self._printer = Print_Iface()  # HAS-A relationship (composition)

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
        
        # Record initial point
        self._printer.print_update(self._x, self._y, self._vx, self._vy)
        self.move(step, user_grav)

        xs = []
        ys = []

        while self.getY() > 1e-14:
            xs.append(self.getX())
            ys.append(self.getY())
            
            # Record plot point using composed printer
            self._printer.print_update(self.getX(), self.getY(), self._vx, self._vy)
            
            self.move(step, user_grav)
        
        # Record final point
        self._printer.print_update(self.getX(), self.getY(), self._vx, self._vy)

        return xs, ys


## Crazyball class - inherits from Cannonball (IS-A relationship)
#  Adds random trajectory variations
#
class Crazyball(Cannonball):
    ## Create a new crazyball at the provided x position.
    #  @param x the x position of the ball
    #
    def __init__(self, x):
        super().__init__(x)
        self.rand_q = 0
    
    ## Override move method to add randomness based on conditions
    #  @param sec the amount of time that has elapsed
    #  @param grav the gravitational constant
    #
    def move(self, sec, grav):
        # Generate random value for condition checking
        self.rand_q = random.randrange(0, 10)
        
        # Check condition (x < 400 as per assignment)
        if self.getX() < 400:
            # Add random variation to trajectory
            random_factor = random.uniform(-2, 2)  # Random variation between -2 and 2
            random_vertical = random.uniform(-1, 1)  # Random vertical variation
            
            # Apply random variations to velocities
            self._vx += random_factor * sec
            self._vy += random_vertical * sec
        
        # Call parent move method
        super().move(sec, grav)
    
    ## Override shoot method to indicate crazy mode
    #
    def shoot(self, angle, velocity, user_grav, step=0.1):
        print("\n🎲 CRAZY MODE ACTIVATED - Random trajectory enabled! 🎲")
        return super().shoot(angle, velocity, user_grav, step)


def run_app():
    st.title("Cannonball Trajectory - Version 2.0")
    st.markdown("---")

    angle_deg = st.number_input(
        "Starting angle (degrees)", min_value=0.0, max_value=90.0, value=45.0
    )
    velocity = st.selectbox("Initial velocity", options=[15, 25, 40], index=1)

    # Updated gravity options with Moon gravity
    gravity_options = {
        "Earth": 9.81,
        "Moon": 1.62  # Moon's gravity is about 1/6 of Earth's
    }
    
    # Add Crazy mode option
    simulation_mode = st.radio(
        "Simulation Mode",
        options=["Normal", "Crazy"],
        index=0,
        help="Crazy mode adds random variations to the trajectory"
    )
    
    gravity_name = st.selectbox("Gravity", options=list(gravity_options.keys()), index=0)
    gravity = gravity_options[gravity_name]
    step = 0.1

    col1, col2 = st.columns(2)
    simulate = col1.button("Simulate")
    
    # Display info about selected mode
    if simulation_mode == "Crazy":
        st.info("🎲 Crazy mode selected: Trajectory will have random variations!")
    if gravity_name == "Moon":
        st.info("🌕 Moon gravity selected: Ball will travel much farther!")

    if simulate:
        angle_rad = radians(angle_deg)
        
        # Choose ball type based on simulation mode
        if simulation_mode == "Crazy":
            ball = Crazyball(0)  # Using inheritance
            st.write("### 🎲 Crazy Ball Trajectory")
        else:
            ball = Cannonball(0)  # Normal ball
            st.write("### 🎯 Normal Ball Trajectory")
        
        xs, ys = ball.shoot(angle_rad, velocity, gravity, step)

        if not xs:
            st.warning("No trajectory points were generated.")
            return

        df = pd.DataFrame({"x": xs, "y": ys})

        # Adjust chart domains based on gravity
        max_x = max(xs) if xs else 200
        max_y = max(ys) if ys else 100
        
        # Add some padding to the domains
        x_domain = [0, max(200, max_x * 1.1)]
        y_domain = [0, max(100, max_y * 1.1)]

        chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("x:Q", scale=alt.Scale(domain=x_domain), title="Distance (m)"),
                y=alt.Y("y:Q", scale=alt.Scale(domain=y_domain), title="Height (m)")
            )
            .properties(width=700, height=400)
        )
        
        # Add points to make crazy trajectory more visible
        if simulation_mode == "Crazy":
            points = alt.Chart(df).mark_point(color='red', size=20).encode(
                x='x:Q',
                y='y:Q'
            )
            chart = chart + points
        
        st.altair_chart(chart, use_container_width=True)
        
        # Display statistics
        st.write("### 📊 Trajectory Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Height", f"{max(ys):.1f} m")
        with col2:
            st.metric("Distance", f"{max(xs):.1f} m")
        with col3:
            st.metric("Gravity", f"{gravity} m/s²")


if __name__ == "__main__":
    run_app()