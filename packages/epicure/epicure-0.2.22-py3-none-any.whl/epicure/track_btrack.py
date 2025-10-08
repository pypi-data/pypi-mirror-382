"""
 Track with btrack package
 https://github.com/quantumjot/btrack/tree/main
"""

import btrack as bt
        self.track_choice.addItem("BTrack")
        self.create_btrack()
        layout.addWidget(self.gBTrack)

############ BTrack option

    def create_btrack(self):
        """ GUI of the BTrack option """
        self.gBTrack, gb_layout = wid.group_layout( "BTrack" )
        featlab = wid.label( "Include features:" )
        gb_layout.addWidget(featlab)
        self.check_area = wid.check( "Area", True, "Include area of the label in the tracking" )
        gb_layout.addLayout(self.check_area)
        self.gBTrack.setLayout(gb_layout)

    def go_btrack( self, start_frame, end_frame ):
        """ Run BTrack on the selected frames """
        self.btrack = BTrack( self.track, self.epicure )
        props = ()
        if self.check_area.isChecked():
            props = props + ("area",)
        btobj = self.btrack.prepare_objects(self.epicure.seg[start_frame:end_frame+1], props )
        self.btrack.track( btobj )



class BTrack():

    def __init__(self, track, epic):
        self.track = track
        self.epicure = epic
        self.tracker = bt.BayesianTracker()
        bt.configure_from_file("btrack_config.json")
        bt.max_search_radius = 10

    def prepare_objects( self, movie, region_props ):
        """ Prepare the movie (stack of label images) for BTrack format """
        obj = bt.utils.segmentation_to_objects( movie, properties=region_props )
        print(obj)
        return obj



    def track(self, obj, **kwargs):
        """ Track the regions """
        return self.tracker.track(regions, **kwargs)