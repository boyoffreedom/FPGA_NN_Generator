import codecs

def PRAM_gen(path,cell_n):
    with codecs.open(path+'/NN_CORE/R_PRAM.v','w', encoding='utf-8') as f:
        f.write(u'`include "extern.v"\n\n')
        f.write(u'module R_PRAM(clk,rst_n,\n')
        f.write(u'\tda_wen, da_addr, da_sel, da_din, da_dout, da_bout,\n')
        f.write(u'\tdw_wen, dw_addr, dw_sel, dw_din, dw_dout, dw_bout);\n\n')
        f.write(u'input clk,rst_n;\n')
        f.write(u'input[`CELL_N-1:0] da_wen,dw_wen;\n')
        f.write(u'input [`DA_AWIDTH-1:0] da_addr;\n')
        f.write(u'input [`DW_AWIDTH-1:0] dw_addr;\n\n')
        f.write(u'input [`CELL_N-1:0] da_sel;\n')
        f.write(u'input [`CELL_N-1:0] dw_sel;\n\n')
        f.write(u'input [`D_LEN-1:0] da_din,dw_din;\n')
        f.write(u'output [`D_LEN-1:0] da_dout,dw_dout;\n')
        f.write(u'output [`DWIDTH-1:0] da_bout,dw_bout;\n\n')

        for i in range(cell_n):
            f.write(u'reg [`D_LEN-1:0] da_%d,dw_%d;\n'%(i,i))
        f.write(u'\n//并置输出\n')
        f.write(u'assign da_bout = {')
        for i in range(cell_n-1,0,-1):
            f.write(u'da_%d, '%i)
        f.write(u'da_0};\n')
        f.write(u'assign dw_bout = {')
        for i in range(cell_n - 1, 0, -1):
            f.write(u'dw_%d, ' % i)
        f.write(u'dw_0};\n\n')

        f.write(u'assign da_dout = ({`D_LEN{da_sel[0]}})&da_0|\n')
        for i in range(1,cell_n-1):
            f.write(u'\t\t\t\t({`D_LEN{da_sel[%d]}})&da_%d|\n'%(i,i))
        f.write(u'\t\t\t\t({`D_LEN{da_sel[%d]}})&da_%d;\n\n'%(cell_n-1,cell_n-1))

        f.write(u'assign dw_dout = ({`D_LEN{dw_sel[0]}})&dw_0|\n')
        for i in range(1, cell_n - 1):
            f.write(u'\t\t\t\t({`D_LEN{dw_sel[%d]}})&dw_%d|\n' % (i, i))
        f.write(u'\t\t\t\t({`D_LEN{dw_sel[%d]}})&dw_%d;\n\n' % (cell_n-1, cell_n-1))

        for i in range(cell_n):
            f.write(u'reg [`D_LEN-1:0] DA_RAM_%d [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a%d.mif" */;\n' % (i, i))
            f.write(u'reg [`D_LEN-1:0] DW_RAM_%d [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w%d.mif" */;\n\n' % (i, i))
        for i in range(cell_n):
            f.write(u'//group%d\n'%i)
            f.write(u'always @(posedge clk) begin\n')
            f.write(u'\tda_%d <= DA_RAM_%d[da_addr];\n'%(i,i))
            f.write(u'\tif(da_wen[%d]) begin\n'%i)
            f.write(u'\t\tDA_RAM_%d[da_addr] <= da_din;\n' % i)
            f.write(u'\tend\nend\n\n')

            f.write(u'\nalways @(posedge clk) begin\n')
            f.write(u'\tdw_%d <= DW_RAM_%d[dw_addr];\n' % (i, i))
            f.write(u'\tif(dw_wen[%d]) begin\n' % i)
            f.write(u'\t\tDW_RAM_%d[dw_addr] <= dw_din;\n' % i)
            f.write(u'\tend\nend\n\n')
        f.write(u'endmodule\n\n')

if __name__ == '__main__':
    R_SEL_gen('./',10)
