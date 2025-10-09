import requests
import json
import pandas as pd
from tkinter import ttk, Tk, StringVar, Label, Entry, Button, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

def EasyInf():
    """
    软件版本信息。
    """
    inf = {
        '软件名称': 'FDA药品不良反应事件查询工具 V1.0',
        '版本号': '1.0.0',
        '功能介绍': 'FDA药品不良反应事件查询。',
        'PID': 'FDADRUGAE001',
        '分组': '药物警戒',
        '依赖': 'requests',
        '资源库版本':'20250804'    
    }
    return inf

class FDAQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FDA药品不良反应事件查询工具 V1.0")
        self.root.geometry("800x600")
        # 获取屏幕尺寸并居中窗口
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = 800  # 窗口宽度
        wh = 600  # 窗口高度
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")
        
        # 创建变量
        self.medication_name = StringVar(value="aspirin")
        self.start_date = StringVar(value="20250101")
        self.end_date = StringVar(value="20250130")
        self.limit = StringVar(value="1000")
        self.result_text = StringVar()
        
        # 创建UI元素
        self.create_widgets()
    
    def create_widgets(self):
        # 输入框框架
        input_frame = ttk.LabelFrame(self.root, text="查询参数", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # 药品名称
        ttk.Label(input_frame, text="药品名称（英文）:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.medication_name, width=40).grid(row=0, column=1, sticky="ew", pady=2)
        
        # 开始日期
        ttk.Label(input_frame, text="开始日期(YYYYMMDD):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.start_date, width=15).grid(row=1, column=1, sticky="w", pady=2)
        
        # 结束日期
        ttk.Label(input_frame, text="结束日期(YYYYMMDD):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.end_date, width=15).grid(row=2, column=1, sticky="w", pady=2)
        
        # 结果限制
        ttk.Label(input_frame, text="返回个例结果数量:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.limit, width=10).grid(row=3, column=1, sticky="w", pady=2)
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # 查询个例按钮
        ttk.Button(button_frame, text="查询个例", command=self.query_individual_cases).pack(side="left", padx=5)
        
        # 导出个例按钮
        ttk.Button(button_frame, text="导出个例信息", command=self.export_individual_cases).pack(side="left", padx=5)
        
        # 查询汇总按钮
        ttk.Button(button_frame, text="查询汇总信息", command=self.query_summary).pack(side="left", padx=5)
        
        # 导出汇总按钮
        ttk.Button(button_frame, text="导出汇总信息", command=self.export_summary).pack(side="left", padx=5)
        # 导出汇总按钮
        ttk.Button(button_frame, text="关于", command=self.about).pack(side="left", padx=5)
        
        # 结果展示
        result_frame = ttk.LabelFrame(self.root, text="查询结果", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_textbox = ScrolledText(result_frame, wrap="word", font=('Consolas', 10))
        self.result_textbox.pack(fill="both", expand=True)
    
    def validate_inputs(self):
        try:
            limit = int(self.limit.get())
            if limit <= 0:
                raise ValueError("结果数量必须大于0")
            if limit > 1000:
                raise ValueError("结果数量不能超过1000")
            
            # 验证日期格式
            datetime.strptime(self.start_date.get(), "%Y%m%d")
            datetime.strptime(self.end_date.get(), "%Y%m%d")
            return True
        except ValueError as e:
            messagebox.showerror("输入错误", f"请输入有效的参数: {str(e)}")
            return False
    
    def make_api_request(self, url, params):
        headers = {
            "User-Agent": "FDA Query Tool/1.0",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=headers,
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"请求出错: {e}\n"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"状态码: {e.response.status_code}\n"
                error_msg += f"响应内容: {e.response.text}\n"
            self.result_textbox.insert("end", error_msg)
            return None
    
    def get_total_report_count(self):
        """获取当前查询条件下的总报告数量"""
        url = "https://api.fda.gov/drug/event.json"
        search_query = f"patient.drug.medicinalproduct:{self.medication_name.get()} AND receivedate:[{self.start_date.get()} TO {self.end_date.get()}]"
        
        params = {
            "search": search_query,
            "count": "patient.reaction.reactionmeddrapt.exact"
        }
        
        data = self.make_api_request(url, params)
        if data is None:
            return 0
        
        # 计算所有分类的总和
        total = sum(item.get('count', 0) for item in data.get('results', []))
        return total

    def about(self):
        messagebox.showinfo("关于", f"本程序属于EasyPV组件，仅供测试使用，联系开发者：411703730@qq.com")

    def query_individual_cases(self):
        if not self.validate_inputs():
            return
        
        # 先检查总报告数量
        self.result_textbox.delete(1.0, "end")
        self.result_textbox.insert("end", "正在检查总报告数量...\n")
        self.root.update()
        
        total_count = self.get_total_report_count()
        
        if total_count > 1000:
            message = (f"当前查询条件共有 {total_count} 条报告，超过系统限制 (1000条)。\n\n"
                      "建议缩小查询时间范围，分多次查询导出。\n\n"
                      "是否继续查询前1000条结果？")
            
            if not messagebox.askyesno("报告数量过多", message):
                return
        
        # 构建查询URL
        url = "https://api.fda.gov/drug/event.json"
        search_query = f"patient.drug.medicinalproduct:{self.medication_name.get()} AND receivedate:[{self.start_date.get()} TO {self.end_date.get()}]"
        
        params = {
            "search": search_query,
            "limit": min(int(self.limit.get()), 1000)  # 确保不超过1000
        }
        
        self.result_textbox.delete(1.0, "end")
        self.result_textbox.insert("end", f"当前查询共有 {total_count} 条报告，正在查询个例...\n")
        self.root.update()
        
        data = self.make_api_request(url, params)
        if data is None:
            return
        
        results = data.get("results", [])
        
        # 显示前5条结果
        self.result_textbox.delete(1.0, "end")
        self.result_textbox.insert("end", f"查询成功，返回{len(results)}条结果（共{total_count}条，显示前5条）：\n\n")
        
        display_count = min(5, len(results))
        for i in range(display_count):
            self.result_textbox.insert("end", f"=== 个例 {i+1} ===\n")
            formatted_json = json.dumps(results[i], indent=4, ensure_ascii=False)
            self.result_textbox.insert("end", formatted_json + "\n\n")
        
        # 保存所有结果以备导出
        self.last_individual_results = results
    
    def export_individual_cases(self):
        if not hasattr(self, 'last_individual_results') or not self.last_individual_results:
            messagebox.showwarning("无数据", "没有可导出的个例数据，请先执行查询")
            return
        
        try:
            # 将结果转换为DataFrame
            df_full = pd.json_normalize(self.last_individual_results)
            
            # 创建简化版DataFrame
            simplified_data = []
            for result in self.last_individual_results:
                # 安全地获取药品信息
                drugs = result.get("patient", {}).get("drug", [])
                drug = drugs[0] if drugs else {}
                
                # 安全地获取患者信息
                patient = result.get("patient", {})
                
                simplified = {
                    "safetyreportid": result.get("safetyreportid", ""),
                    "receivedate": result.get("receivedate", ""),
                    "medicinalproduct": drug.get("medicinalproduct", ""),
                    "reactionmeddrapt": ", ".join([r.get("reactionmeddrapt", "") for r in patient.get("reaction", [])]),
                    "patientage": patient.get("patientonsetage", ""),
                    "patientsex": patient.get("patientsex", ""),
                    "seriousnessdeath": result.get("seriousnessdeath", ""),
                    "seriousnesshospitalization": result.get("seriousnesshospitalization", ""),
                }
                simplified_data.append(simplified)
            
            df_simplified = pd.DataFrame(simplified_data)
            
            # 弹出保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
                title="保存个例信息"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df_full.to_excel(writer, sheet_name='完整数据', index=False)
                    df_simplified.to_excel(writer, sheet_name='简化数据', index=False)
                
                messagebox.showinfo("导出成功", f"个例信息已成功导出到:\n{file_path}\n包含完整数据和简化数据两个工作表")
                
        except Exception as e:
            messagebox.showerror("导出错误", f"导出过程中出错: {str(e)}\n\n建议检查数据格式是否正确。")
    
    def query_summary(self):
        if not self.validate_inputs():
            return
        
        self.result_textbox.delete(1.0, "end")
        self.result_textbox.insert("end", "正在查询汇总信息，请稍候...\n")
        self.root.update()
        
        # 构建基础查询条件
        base_query = f"patient.drug.medicinalproduct:{self.medication_name.get()} AND receivedate:[{self.start_date.get()} TO {self.end_date.get()}]"
        
        # 定义三个汇总查询
        queries = [
            {
                "name": "不良反应类型统计",
                "url": "https://api.fda.gov/drug/event.json",
                "params": {
                    "search": base_query,
                    "count": "patient.reaction.reactionmeddrapt.exact"
                }
            },
            {
                "name": "药品名称统计",
                "url": "https://api.fda.gov/drug/event.json",
                "params": {
                    "search": base_query,
                    "count": "patient.drug.medicinalproduct.exact"     
                }
            },
            {
                "name": "严重性统计",
                "url": "https://api.fda.gov/drug/event.json",
                "params": {
                    "search": base_query,
                    "count": "serious.exact"
                }
            }            
        ]
        
        self.summary_results = {}
        
        for query in queries:
            self.result_textbox.insert("end", f"\n=== 正在查询 {query['name']} ===\n")
            self.root.update()
            
            data = self.make_api_request(query['url'], query['params'])
            if data is None:
                continue
            
            self.summary_results[query['name']] = data
            
            # 显示结果
            count_data = data.get('results', [])
            self.result_textbox.insert("end", f"{query['name']}结果:\n")
            
            for item in count_data:
                term = item.get('term', '未知')
                count = item.get('count', 0)
                self.result_textbox.insert("end", f"{term}: {count} 例\n")
    
    def export_summary(self):
        if not hasattr(self, 'summary_results') or not self.summary_results:
            messagebox.showwarning("无数据", "没有可导出的汇总数据，请先执行查询")
            return
        
        try:
            # 创建DataFrame列表
            dfs = []
            
            for name, data in self.summary_results.items():
                count_data = data.get('results', [])
                df = pd.DataFrame(count_data)
                df['统计类型'] = name  # 添加统计类型列
                dfs.append(df)
            
            # 合并所有DataFrame
            combined_df = pd.concat(dfs, ignore_index=True)
            
            # 按统计类型分组创建不同的工作表
            grouped = combined_df.groupby('统计类型')
            
            # 弹出保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
                title="保存汇总信息"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    for name, group in grouped:
                        # 清理工作表名称（Excel限制31字符且不能包含特殊字符）
                        sheet_name = name[:31].replace(':', '').replace('\\', '').replace('/', '').replace('?', '').replace('*', '').replace('[', '').replace(']', '')
                        group.to_excel(writer, sheet_name=sheet_name, index=False)
                
                messagebox.showinfo("导出成功", f"汇总信息已成功导出到:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("导出错误", f"导出过程中出错: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = FDAQueryApp(root)
    root.mainloop()
