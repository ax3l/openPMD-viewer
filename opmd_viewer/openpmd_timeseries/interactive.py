"""
This file is part of the OpenPMD viewer

It defines an interactive interface for the viewer,
based on the IPython notebook functionalities
"""
try:
    from ipywidgets import widgets
except ImportError:
    # If ipywidgets is not available, use the deprecated package
    # IPython.html.widgets, so that the GUI still works
    from IPython.html import widgets

from IPython.display import display, clear_output
import math
import matplotlib
import matplotlib.pyplot as plt

class InteractiveViewer(object):

    def __init__(self) :
        pass

    def slider(self, figsize=(10,10), **kw) :
        """
        Navigate the simulation using a slider

        Parameters :
        ------------
        figsize: tuple
            Size of the figures

        kw: dict
            Extra arguments to pass to matplotlib's imshow
        """

        # -----------------------
        # Define useful functions
        # -----------------------

        def refresh_field(force=False) :
            "Refresh the current field figure"
            
            # Determine whether to do the refresh
            do_refresh = False
            if (self.avail_fields is not None):
                if force == True or fld_refresh_toggle.value == True:
                    do_refresh = True
            # Do the refresh
            if do_refresh == True :
                plt.figure(fld_figure_button.value, figsize=figsize)
                plt.clf()

                # When working in inline mode, in an ipython notebook,
                # clear the output (prevents the images from stacking
                # in the notebook)
                if 'inline' in matplotlib.get_backend() :
                    clear_output()

                if fld_use_button.value == True :
                    i_power = fld_magnitude_button.value
                    vmin = fld_range_button.value[0]*10**i_power
                    vmax = fld_range_button.value[1]*10**i_power
                else :
                    vmin = None
                    vmax = None
                
                self.get_field( t=self.current_t, output=False, plot=True,
                    field=fieldtype_button.value, coord=coord_button.value,
                    m=convert_to_int( mode_button.value ),
                    slicing=slicing_button.value, theta=theta_button.value,
                    slicing_dir=slicing_dir_button.value,
                    vmin=vmin, vmax=vmax, cmap=fld_color_button.value )
                
        def refresh_ptcl(force=False) :
            "Refresh the current particle figure"
            
            # Determine whether to do the refresh
            do_refresh = False
            if self.avail_species is not None:
                if force == True or ptcl_refresh_toggle.value == True:
                    do_refresh = True
            # Do the refresh
            if do_refresh == True :
                plt.figure(ptcl_figure_button.value, figsize=figsize)
                plt.clf()

                # When working in inline mode, in an ipython notebook,
                # clear the output (prevents the images from stacking
                # in the notebook)
                if 'inline' in matplotlib.get_backend() :
                    clear_output()
                
                if ptcl_use_button.value == True :
                    i_power = ptcl_magnitude_button.value
                    vmin = ptcl_range_button.value[0]*10**i_power
                    vmax = ptcl_range_button.value[1]*10**i_power
                else :
                    vmin = None
                    vmax = None
                    
                if ptcl_yaxis_button.value == 'None':
                    # 1D histogram
                    self.get_particle( t=self.current_t, output=False,
                        var_list=[ptcl_xaxis_button.value],
                        select=ptcl_select_widget.to_dict(),
                        species=ptcl_species_button.value, plot=True, 
                        vmin=vmin, vmax=vmax, cmap=ptcl_color_button.value,
                        nbins=ptcl_bins_button.value )
                else :
                    # 2D histogram
                    self.get_particle( t=self.current_t, output=False,
                        var_list=[ptcl_xaxis_button.value,
                                  ptcl_yaxis_button.value],
                        select=ptcl_select_widget.to_dict(),
                        species=ptcl_species_button.value, plot=True,
                        vmin=vmin, vmax=vmax, cmap=ptcl_color_button.value,
                        nbins=ptcl_bins_button.value )
                
        def refresh_ptcl_now(b):
            "Refresh the particles immediately"
            refresh_ptcl(force=True)

        def refresh_fld_now(b):
            "Refresh the fields immediately"
            refresh_field(force=True)

        def change_t( name, value ) :
            "Plot the result at the required time"
            self.current_t = 1.e-15*value
            refresh_field()
            refresh_ptcl()

        def step_fw(b) :
            "Plot the result one iteration further"
            if self.current_i < len(self.t) - 1 :
                self.current_t = self.t[self.current_i+1]
            else :
                print("Reached last iteration.")
                self.current_t = self.t[self.current_i]
            slider.value = self.current_t*1.e15

        def step_bw(b) :
            "Plot the result one iteration before"
            if self.current_t > 0 :
                self.current_t = self.t[self.current_i-1]
            else :
                print("Reached first iteration.")
                self.current_t= self.t[self.current_i]
            slider.value = self.current_t*1.e15

        # ---------------
        # Define widgets
        # ---------------

        # Slider
        slider = widgets.FloatSlider(
            min=math.ceil(1.e15*self.tmin),
            max=math.ceil(1.e15*self.tmax),
            step=math.ceil(1.e15*(self.tmax-self.tmin))/20.,
            description="t (fs)")
        slider.on_trait_change( change_t, 'value' )

        # Forward button
        button_p = widgets.Button(description="+")
        button_p.on_click(step_fw)

        # Backward button
        button_m = widgets.Button(description="-")
        button_m.on_click(step_bw)

        # Display the time widgets
        container = widgets.HBox(children=[ button_m, button_p, slider ])
        display(container)

        # Field widgets
        # -------------
        if (self.avail_fields is not None) :

            # Field type
            # ----------
            # Field button
            fieldtype_button = widgets.ToggleButtons(
                description='Field:',
                options=sorted(self.avail_fields.keys()))
            fieldtype_button.on_trait_change( refresh_field )

            # Coord button
            if self.geometry == "thetaMode":
                coord_button = widgets.ToggleButtons(
                    description='Coord:', options=['x', 'y', 'z', 'r', 't'] )
            elif self.geometry in ["2dcartesian", "3dcartesian"] :
                coord_button = widgets.ToggleButtons(
                    description='Coord:', options=['x', 'y', 'z'] )
            coord_button.on_trait_change( refresh_field )
            # Mode and theta button (for thetaMode)
            mode_button = widgets.ToggleButtons( description='Mode:',
                            options=self.avail_circ_modes )
            mode_button.on_trait_change( refresh_field )
            theta_button = widgets.FloatSlider( width=140, value=0.,
                    description=r'Theta:', min=-math.pi/2, max=math.pi/2 )
            theta_button.on_trait_change( refresh_field )
            # Slicing buttons (for 3D)
            slicing_dir_button = widgets.ToggleButtons( value='y',
                description='Slicing direction:', options=['x', 'y', 'z'] )
            slicing_dir_button.on_trait_change( refresh_field )
            slicing_button = widgets.FloatSlider( width=150,
                description='Slicing:', min=-1., max=1., value=0. )
            slicing_button.on_trait_change( refresh_field )

            # Plotting options
            # ----------------
            # Figure number
            fld_figure_button = widgets.IntText( description='Figure ',
                                        value=0, width=50)
            # Range of values
            fld_range_button = widgets.FloatRangeSlider(
                min=-10, max=10, width=220 )
            fld_range_button.on_trait_change( refresh_field )
            # Order of magnitude
            fld_magnitude_button = widgets.IntText(
                description='x 10^', value=9, width=50)
            fld_magnitude_button.on_trait_change( refresh_field )
            # Use button
            fld_use_button = widgets.Checkbox(
                description=' Use this range', value=False)
            fld_use_button.on_trait_change( refresh_field )
            # Colormap button
            fld_color_button = widgets.Select(
                options=sorted(plt.cm.datad.keys()), height=50, width=200,
                value='jet' )
            fld_color_button.on_trait_change( refresh_field )
            # Resfresh buttons
            fld_refresh_toggle = widgets.ToggleButton(
                description='Always refresh', value=True) 
            fld_refresh_button = widgets.Button(
                description='Refresh now!')
            fld_refresh_button.on_click( refresh_fld_now )            

            # Containers
            # ----------
            # Field type container
            if self.geometry == "thetaMode" :
                container_fields = widgets.VBox( width=260, 
                    children=[fieldtype_button, coord_button,
                              mode_button, theta_button] )
            elif self.geometry == "2dcartesian":
                container_fields = widgets.VBox( width=260,
                    children=[fieldtype_button, coord_button] )
            elif self.geometry == "3dcartesian":
                container_fields = widgets.VBox( width=260,
                    children=[fieldtype_button, coord_button,
                    slicing_dir_button, slicing_button ] )
            # Plotting options container
            container_fld_plots = widgets.VBox( width=260,
                children=[ fld_figure_button, fld_range_button,
            widgets.HBox( children=[ fld_magnitude_button, fld_use_button],
                          height=50 ), fld_color_button ] )
            # Accordion for the field widgets
            accord1 = widgets.Accordion(
                children=[container_fields, container_fld_plots] )
            accord1.set_title(0, 'Field type')
            accord1.set_title(1, 'Plotting options')
            # Complete field container
            container_fld =  widgets.VBox( width=300,
                children=[ accord1, widgets.HBox(
                    children=[ fld_refresh_toggle, fld_refresh_button]) ])
            

        # Particle widgets
        # ----------------
        if (self.avail_species is not None):
            
            # Particle quantities
            # -------------------         
            # Species selection
            ptcl_species_button = widgets.Dropdown( width=250,
                options=self.avail_species )
            ptcl_species_button.on_trait_change( refresh_ptcl )
            # Remove charge and mass (less interesting) 
            avail_ptcl_quantities = [ q for q in self.avail_ptcl_quantities \
                        if (q in ['charge', 'mass'])==False ]
            # Particle quantity on the x axis
            ptcl_xaxis_button = widgets.ToggleButtons(
                value='z', options=avail_ptcl_quantities )
            ptcl_xaxis_button.on_trait_change( refresh_ptcl )
            # Particle quantity on the y axis            
            ptcl_yaxis_button = widgets.ToggleButtons(
                value='x', options=avail_ptcl_quantities+['None'] )
            ptcl_yaxis_button.on_trait_change( refresh_ptcl )

            # Particle selection
            # ------------------
            # 3 selection rules at maximum
            ptcl_select_widget = ParticleSelectWidget(3,
                                avail_ptcl_quantities, refresh_ptcl)

            # Plotting options
            # ----------------
            # Figure number
            ptcl_figure_button = widgets.IntText( description='Figure ',
                                            value=1, width=50 )
            # Number of bins
            ptcl_bins_button = widgets.IntSlider( description='nbins:',
                            min=50, max=300, value=100, width=150 )
            ptcl_bins_button.on_trait_change( refresh_ptcl )
            # Colormap button
            ptcl_color_button = widgets.Select( 
                options=sorted(plt.cm.datad.keys()), height=50, width=200,
                value='Blues' )
            ptcl_color_button.on_trait_change( refresh_ptcl )
            # Range of values
            ptcl_range_button = widgets.FloatRangeSlider(
                min=0, max=10, width=220, value=(0,5) )
            ptcl_range_button.on_trait_change( refresh_ptcl )
            # Order of magnitude
            ptcl_magnitude_button = widgets.IntText(
                description='x 10^', value=9, width=50)
            ptcl_magnitude_button.on_trait_change( refresh_ptcl )
            # Use button
            ptcl_use_button = widgets.Checkbox(
                description=' Use this range', value=False)
            ptcl_use_button.on_trait_change( refresh_ptcl )
            # Resfresh buttons
            ptcl_refresh_toggle = widgets.ToggleButton(
                description='Always refresh', value=True) 
            ptcl_refresh_button = widgets.Button(
                description='Refresh now!')
            ptcl_refresh_button.on_click( refresh_ptcl_now )
            
            # Containers
            # ----------
            # Particle quantity container
            container_ptcl_quantities = widgets.VBox( width=310,
                children=[ ptcl_species_button, ptcl_xaxis_button,
                           ptcl_yaxis_button] )
            # Particle selection container
            container_ptcl_select = ptcl_select_widget.to_container()
            # Plotting options container
            container_ptcl_plots = widgets.VBox( width=310,
            children=[ ptcl_figure_button, ptcl_bins_button, ptcl_range_button,
            widgets.HBox(children=[ ptcl_magnitude_button, ptcl_use_button],
                         height=50), ptcl_color_button ])
            # Accordion for the field widgets
            accord2 = widgets.Accordion(
            children=[container_ptcl_quantities, container_ptcl_select,
                      container_ptcl_plots] )
            accord2.set_title(0, 'Particle quantities')
            accord2.set_title(1, 'Particle selection')
            accord2.set_title(2, 'Plotting options')
            # Complete particle container
            container_ptcl =  widgets.VBox( width=370,
                children=[ accord2, widgets.HBox(
                    children=[ ptcl_refresh_toggle, ptcl_refresh_button]) ])

        # Global container
        if (self.avail_fields is not None) and \
          (self.avail_species is not None):
            global_container = widgets.HBox(
                children=[ container_fld, container_ptcl])
            display(global_container)
        elif self.avail_species is None:
            display( container_fld )
        elif self.avail_fields is None:
            display( container_ptcl )

def convert_to_int( m ):
    """
    Convert the string m to an int, except if m is 'all' or None
    """
    if (m=='all') or (m is None):
        return(m)
    else:
        return( int(m) )



class ParticleSelectWidget(object):
    """
    Class that groups the particle selection widgets.
    """

    def __init__( self, n_rules, avail_ptcl_quantities, refresh_ptcl):
        """
        Initialize a set of particle selection widgets

        Parameters:
        -----------
        n_rules: int
            The number of selection rules to display

        avail_ptcl_quantities: list of string
            The particle quantities in the present openPMD timeseries

        refresh_ptcl: callable
            The callback function to execute when the widget is changed
        """
        self.n_rules = n_rules
        
        # Create widgets that determines whether the rule is used
        self.active = [ widgets.Checkbox(value=False) \
                         for i in range(n_rules) ]
        # Create widgets that determines the quantity on which to select
        self.quantity = [ widgets.Dropdown(options=avail_ptcl_quantities,
                            description='Select ') for i in range(n_rules) ]
        # Create widgets that determines the lower bound and upper bound
        self.low_bound = [ widgets.FloatText( value=-1.e-1, width = 90,
                    description='from ') for i in range(n_rules) ]
        self.up_bound = [ widgets.FloatText( value=1.e-1, width = 90,
                    description='to ') for i in range(n_rules) ]

        # Add the callback function refresh_ptcl to each widget
        for i in range(n_rules):
            self.active[i].on_trait_change( refresh_ptcl )
            self.quantity[i].on_trait_change( refresh_ptcl )
            self.low_bound[i].on_trait_change( refresh_ptcl )
            self.up_bound[i].on_trait_change( refresh_ptcl )

    def to_container( self ):
        """
        Return a widget container, where all the particle selection
        widgets are placed properly, with respect to each other.
        """
        containers = []
        for i in range(self.n_rules):
            containers.append( widgets.HBox( height=40,
                children=[self.active[i], self.quantity[i]] ))
            containers.append( widgets.HBox( height=50, 
                children=[self.low_bound[i], self.up_bound[i]] ))

        return( widgets.VBox( children=containers, width=310 ) )

    def to_dict( self ):
        """
        Return a selection dictionary of the form
        {'uz': [-0.1, 2.], 'x':[-10., 10.]}
        depending on the values of the widgets.
        """
        rule_dict = {}
        # Go through the selection rules and add the active rules
        for i in range( self.n_rules ):
            if self.active[i].value is True:
                rule_dict[ self.quantity[i].value ] = \
                    [ self.low_bound[i].value, self.up_bound[i].value ]

        # If any rule is active, return a dictionary
        if len(rule_dict) != 0:
            return(rule_dict)
        # If no rule is active, return None
        else:
            return(None)
