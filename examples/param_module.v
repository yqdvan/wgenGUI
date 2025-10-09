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
    input      [DATA_WIDTH-1:0] data_in,
    
    // 输出端口
    output reg [DATA_WIDTH-1:0] data_out,
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