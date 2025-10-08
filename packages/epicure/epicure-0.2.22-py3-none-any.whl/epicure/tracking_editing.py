from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget
import numpy as np
import epicure.Utils as ut

class trackEditingWidget(QWidget):
    def __init__(self, napari_viewer, epic):
        super().__init__()
        self.viewer = napari_viewer
        self.epicure = epic
        self.suggestion = self.epicure.suggestion
        self.events = self.epicure.events
        
        layout = QVBoxLayout()
        self.btn = QPushButton("Nothing yet", parent=self)
        #self.btn.setEnabled(False)
        layout.addWidget(self.btn)
        self.setLayout(layout)

        self.btn.clicked.connect(self.inspect_oneframe)

    def add_inspect(self, pos, label):
        """ Add a suspicious point (position and label) """
        self.events = self.epicure.events
        self.epicure.add_inspect(pos, label, "tracking")

    def inspect_oneframe(self):
        """ Find suspicious cell that exists in only one frame """
        seg = self.viewer.layers["Segmentation"]
        props = ut.labels_properties( seg.data )
        imshape = seg.data.shape
        self.events.data = np.zeros(imshape, dtype="uint8")
        for prop in props:
            if (prop.bbox[3]-prop.bbox[0]) == 1:
                ## label present only on one frame, inspect
                if (prop.bbox[3] != (imshape[0]-1)) and (prop.bbox[0]!=0):
                    ## not first or last frame
                    if (prop.bbox[1]>0) and (prop.bbox[4]<(imshape[1]-1)):
                        if (prop.bbox[2]>0) and (prop.bbox[5]<(imshape[2]-1)):
                            ## not touching border
                            self.inspect[ seg.data==prop.label ] = 1
        self.show_events()

    def show_events(self):
        self.events.refresh()
        self.show_names( self.suggestion, "SuggestedId" )
        self.epicure.finish_update()

    def show_names(self, lablayer, name):
        ut.remove_layer(self.viewer, name)
        # create the properties dictionary
        properties = ut.labels_bbox( lablayer.data )

        # create the bounding box rectangles
        bbox_rects = self.make_label_bbox([properties[f'bbox-{i}'] for i in range(6)], dim=3)
        if self.viewer.dims.ndisplay == 2:
            transl = [0,0]
        else:
            transl = [0,0,0]

        # specify the display parameters for the text
        text_parameters = {
            'text': '{label}',
            'size': 18,
            'color': 'white',
            'anchor': 'center',
            'translation': transl,
        }

        namelayer = self.viewer.add_shapes(
        bbox_rects,
        face_color='transparent',
        edge_color='gray',
        edge_width = 0,
        properties=properties,
        text=text_parameters,
        name=name,
        )

    def make_label_bbox(self, bbox_extents, dim):
        """Get the coordinates of the corners of a bounding box from the extents

        Parameters
        ----------
        bbox_extents : list (4xN)
            List of the extents of the bounding boxes for each of the N regions.
            Should be ordered: [min_row, min_column, max_row, max_column]

        Returns
        -------
        bbox_rect : np.ndarray
        The corners of the bounding box. Can be input directly into a
        napari Shapes layer.
        """
        if dim == 2:
            minc = bbox_extents[0]
            mint = bbox_extents[1]
            maxc = bbox_extents[2]
            maxt = bbox_extents[3]#*mig.scaleXY
    
            bbox_rect = np.array( [[minc, mint], [minc, maxt], [maxc, maxt], [maxc,mint]] )
        if dim == 3: 
            minr = bbox_extents[0]#*mig.scaleZ
            minc = bbox_extents[1]#*mig.scaleXY
            mint = bbox_extents[2]#*mig.scaleXY
            maxr = bbox_extents[3]-1#*mig.scaleZ
            maxc = bbox_extents[4]#*mig.scaleXY
            maxt = bbox_extents[5]#*mig.scaleXY
            limr = (minr+maxr)/2
    
    
            bbox_rect = np.array( [[limr, minc, mint], [limr, minc, maxt], [limr, maxc, maxt], [limr, maxc,mint]] )
        
        bbox_rect = np.moveaxis(bbox_rect, 2, 0)
        return bbox_rect
        


