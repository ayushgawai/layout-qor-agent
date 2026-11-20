* DFF-lite: two latches, transistor level sketch
.subckt dff D CLK Q VPWR VGND
MP1 N1 CLK VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN1 N1 D VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
MP2 Q N1 VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN2 Q N1 VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
MP3 N2 CLK VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN3 N2 Q VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
.ends
