"""
Tracking by registration with optical flow

"""

import napari
import numpy as np
from skimage.measure import regionprops
from skimage.transform import warp
from skimage.registration import optical_flow_tvl1, optical_flow_ilk
import epicure.Utils as ut
from napari.utils import progress


class trackOptical():

    def __init__(self, track, epic):
        self.min_iou = 0.5
        self.radius = 5
        self.show = False
        self.track = track
        self.epicure = epic

    def set_parameters(self, miniou, radius, show=False):
        self.min_iou = miniou
        self.radius = radius
        self.show = show

    def track_by_optical_flow(self, viewer, start_frame, end_frame):
        """ Registered by optical flow and track by taking best match """
        movie = viewer.layers["Movie"]
        self.seglayer = viewer.layers["Segmentation"]
        self.divisions = {}
        if self.show:
            if "FlowedSegmentation" in self.epicure.viewer.layers:
                ut.remove_layer(self.epicure.viewer, "FlowedSegmentation")
            self.opticaled = self.epicure.viewer.add_labels(np.zeros(self.seglayer.data.shape, dtype=self.epicure.dtype), blending="additive", opacity=0.5, name="FlowedSegmentation")
            self.opticaled.visible = False

        for frame in progress(range(start_frame, end_frame+1)):
            mov = movie.data[frame]
            if (frame >= start_frame) and (frame <= end_frame):
                if frame < (movie.data.shape[0]-1):
                    clabel = self.epicure.get_only_unlocked_labels(frame)
                    nseg_reg = self.register_consecutive_frames( mov, movie.data[frame+1], clabel )
                    if self.show:
                        self.opticaled.data[frame+1,] = np.copy(nseg_reg)
                    next_label = self.epicure.get_only_unlocked_labels(frame+1)
                    matches, orphans = self.match_labels( nseg_reg, next_label )
                    self.update_labels(self.seglayer.data[frame+1], matches, frame+1)
                    if self.track.suspecting:
                        self.examine_orphans( orphans, frame+1 )
        if self.track.suspecting:
            self.suspect_oneframe()
        if self.show:
            self.opticaled.refresh()
        ut.show_info("Tracking done")

    def register_consecutive_frames( self, img0, img1, lab1 ):
        """ Register two consecutives frames and return registered labels """
        ## compute the optical flow
        #v, u = optical_flow_tvl1( img0, img1 )
        v, u = optical_flow_ilk( img0, img1, radius=self.radius )
        ## Apply it to the labels of img1
        nr, nc = img0.shape
        rowc, colc = np.meshgrid( np.arange(nr), np.arange(nc), indexing="ij" )
        lab1_reg = warp( lab1, np.array( [rowc-v, colc-u] ), order=0, mode="edge" )
        return lab1_reg

    def match_labels( self, lab0, lab1 ):
        """ Compare two labels image and find best overlap """
        smooth = 1
        props = regionprops(lab1)
        matches = {}
        orphans = {}
        for prop in props:
            inds = prop.slice
            obj = lab0[inds]*prop.image
            npixels = int(prop.area)
            ## find label in previous frame with best IOU
            if len(np.unique(obj)) >= 2:
                best_iou = 0
                best_lab = None
                best_insideprop = 0
                for olab in np.unique(obj):
                    if olab > 0:
                        inter = np.sum(obj==olab)*1.0
                        union = (np.sum(lab0==olab) + npixels - inter)*1.0
                        iou = (inter) / (union)
                        if iou > best_iou:
                            best_iou = iou
                            best_lab = olab
                            best_insideprop = inter / npixels
                if (best_lab is not None) and (best_iou>self.min_iou):
                    if best_lab in matches:
                        matches[best_lab].append(prop.label)
                    else:
                        matches[best_lab] = [prop.label]
                else:
                    orphans[prop.label] = (best_lab, best_insideprop)
        return matches, orphans


    def update_labels(self, lab, matches, frame):
        """ Change label according to dictionnary """
        oldlabs = np.copy(lab)
        for new_label, old_label in matches.items():
            if len(old_label)==1 and old_label[0] > 0:
                lab[oldlabs==old_label[0]] = new_label
            ## else probable cell division, don't change
            if len(old_label) == 2:
                self.divisions[(new_label, frame)] = old_label
            if len(old_label)>2:
                print(old_label)
                
        oldlabs = None

    def examine_orphans(self, orphans, frame):
        """ Try to see why label was unmatched """
        if frame < (self.seglayer.data.shape[0]-1):
            nextframe = self.seglayer.data[frame+1]
            curframe = self.seglayer.data[frame]
            imshape = nextframe.shape
            for suspect, feats in orphans.items():
                prop = regionprops( (curframe==suspect).astype(np.uint8) )[0]
                ## check that it's not a border cell
                if not ut.outerBBox2D(prop.bbox, imshape):
                    ## label is not present after
                    if np.sum(nextframe==suspect) == 0:
                       self.epicure.suspecting.add_suspect( (frame,)+tuple(prop.centroid), suspect, "tracking") 
                       ## is mostly inside a previous label
                       if self.track.suggesting and feats[1] > 0.75:
                           self.epicure.add_suggestion( suspect, feats[0] )

    def suspect_oneframe(self):
        """ Inspect the list of possible divisions if something suspicious """
        for (parent, frame), events in self.divisions.items():
            haslab = np.sum( self.seglayer.data==events[0], axis=(1,2) )
            # label events[0] is present in only one frame
            if self.track.suggesting and np.sum(haslab>0) <= 1:
                self.suggest_merge(frame, events[0], events[1], parent)
            else:
                # label events[1] is present in only one frame
                haslab = np.sum( self.seglayer.data==events[1], axis=(1,2) )
                if self.track.suggesting and np.sum(haslab>0) <= 1:
                    self.suggest_merge(frame, events[1], events[0], parent)

    def suggest_merge(self, frame, suspect, sister, parent):
        """ Suggest a merge of labels suspect and sister to label parent """
        lab = np.argwhere(self.seglayer.data[frame,]==suspect)
        pos = np.mean(lab, axis=0)
        pos = (frame,)+(int(pos[0]),)+(int(pos[1]),)
        self.epicure.suspecting.add_suspect(pos, suspect, "tracking")
        self.epicure.add_suggestion(suspect, parent)
        self.epicure.add_suggestion(sister, parent)

