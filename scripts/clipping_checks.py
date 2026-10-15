"""Validate the actual WFF rendering crop, including all configurable branches."""

def check_complication_crops(watchface):
    for slot in watchface.findall('Scene/ComplicationSlot'):
        area=slot.find('BoundingBox')
        assert area is not None, 'This face uses rectangular complication render bounds'
        bx,by,bw,bh=[float(area.attrib[a]) for a in ('x','y','width','height')]

        def visit(node, x=0, y=0):
            if node.tag=='Group':
                x+=float(node.attrib.get('x',0));y+=float(node.attrib.get('y',0))
            if node.tag in ('PartText','PartImage','PartDraw'):
                rx=x+float(node.attrib.get('x',0));ry=y+float(node.attrib.get('y',0))
                w=float(node.attrib['width']);h=float(node.attrib['height'])
                assert rx>=bx and ry>=by and rx+w<=bx+bw and ry+h<=by+bh, (
                    f"Slot {slot.attrib['slotId']}: {node.tag} would be cropped by BoundingBox: "
                    f"content={(rx,ry,w,h)}, crop={(bx,by,bw,bh)}")
            for child in node:
                visit(child,x,y)

        for complication in slot.findall('Complication'):
            visit(complication)
