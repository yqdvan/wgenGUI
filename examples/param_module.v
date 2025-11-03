
    // module param_module (clk_i, rst_n, data_in, data_out, bidir_bus);
    //     input clk_i;
    //     input rst_n;
    //     input [7:0] data_in;
    //     output reg [15:0] data_out;
    //     inout [3:0] bidir_bus;
        // 模块内容
//     endmodule


module param_module #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 4
) (
    // 输入端口
    input                     clk,
    input                     rst_n,
    input                     write_en,
    input                     read_en,
    input      [ADDR_WIDTH-1:0] addr,
    input      [100-1:0] data_in,
    
    // 输出端口
    output reg [DATA_WIDTH-1:0] data_out,
    output reg [DATA_WIDTH-1:0] add1_out,
    output reg                 ready
);
    
    // 示例内部逻辑
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_out <= 0;
            ready <= 0;
        end else begin
            if (read_en) begin
                data_out <= {DATA_WIDTH{1'b1}}; // 示例值
                ready <= 1;
            end else begin
                ready <= 0;
            end
        end
    end
    
endmodule