module simple_module (
    // 输入端口
    input clk,
    input rst_n,
    input data_in,
    
    // 输出端口
    output data_out
);
    
    // 简单的逻辑实现
    assign data_out = data_in & clk & rst_n;
    
endmodule