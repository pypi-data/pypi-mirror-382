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
        '软件名称': 'FDA MAUDE设备事件查询工具',
        '版本号': '2.0.0',
        '功能介绍': 'FDA MAUDE设备事件查询。',
        'PID': 'FDAMDRDSLF001',
        '分组': '药物警戒',
        '依赖': 'requests',
        '资源库版本':'20251009'    
    }
    return inf
   
  
class FDAQueryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FDA设备事件查询工具 V2.0")
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
        self.generic_name = StringVar(value="Infusion Pump")
        self.start_date = StringVar(value="20250101")
        self.end_date = StringVar(value="20250130")
        self.limit = StringVar(value="1000")
        self.query_type = StringVar(value="精确查询")  # 新增：查询类型
        self.result_text = StringVar()
        
        # 创建UI元素
        self.create_widgets()
    
    def create_widgets(self):
        # 输入框框架
        input_frame = ttk.LabelFrame(self.root, text="查询参数", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # 设备通用名称
        ttk.Label(input_frame, text="设备通用名称（英文）:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.generic_name, width=40).grid(row=0, column=1, sticky="ew", pady=2)
        
        # 查询类型
        #ttk.Label(input_frame, text="查询类型:").grid(row=1, column=0, sticky="w", pady=2)
        query_type_combo = ttk.Combobox(input_frame, textvariable=self.query_type, 
                                       values=["精确查询", "关联查询"], 
                                       state="readonly", width=15)
        #query_type_combo.grid(row=1, column=1, sticky="w", pady=2)
        
        # 开始日期
        ttk.Label(input_frame, text="开始日期(YYYYMMDD):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.start_date, width=15).grid(row=2, column=1, sticky="w", pady=2)
        
        # 结束日期
        ttk.Label(input_frame, text="结束日期(YYYYMMDD):").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.end_date, width=15).grid(row=3, column=1, sticky="w", pady=2)
        
        # 结果限制
        ttk.Label(input_frame, text="返回个例结果数量:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(input_frame, textvariable=self.limit, width=10).grid(row=4, column=1, sticky="w", pady=2)
        
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
        # 关于按钮
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
    
    def format_search_query(self, generic_name, query_type):
        """格式化搜索查询，根据查询类型处理"""
        date_query = f"date_received:[{self.start_date.get()} TO {self.end_date.get()}]"
        
        if query_type == "精确查询":
            # 精确查询：只匹配设备通用名称
            if ' ' in generic_name:
                device_query = f'device.generic_name:"{generic_name}"'
            else:
                device_query = f'device.generic_name:{generic_name}'
            return f"{device_query} AND {date_query}"
        else:
            # 关联查询：在报告文本中搜索关键词（更广泛的搜索）
            if ' ' in generic_name:
                # 对于包含空格的名称，使用短语搜索
                text_query = f'mdr_text:"{generic_name}"'
            else:
                # 对于单个词，使用通配符搜索
                text_query = f'mdr_text:{generic_name}*'
            
            # 关联查询包括设备名称和报告文本
            if ' ' in generic_name:
                search_terms = [
                    f'device.generic_name:"{generic_name}"',
                    f'device.device_name:"{generic_name}"',
                    text_query,
                    f'product_problems:"{generic_name}"'
                ]
            else:
                search_terms = [
                    f'device.generic_name:{generic_name}',
                    f'device.device_name:{generic_name}',
                    text_query,
                    f'product_problems:{generic_name}'
                ]
            device_query = " OR ".join(search_terms)
            return f"({device_query}) AND {date_query}"
    
    def make_api_request(self, url, params):
        headers = {
            "User-Agent": "FDA Query Tool/1.0",
            "Accept": "application/json"
        }
        
        try:
            # 在请求前显示完整的查询URL，便于调试
            full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            self.result_textbox.insert("end", f"请求URL: {full_url}\n\n")
            self.root.update()
            
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
        url = "https://api.fda.gov/device/event.json"
        search_query = self.format_search_query(self.generic_name.get(), self.query_type.get())
        
        params = {
            "search": search_query,
            "count": "event_type.exact"
        }
        
        data = self.make_api_request(url, params)
        if data is None:
            return 0
        
        # 计算所有分类的总和
        total = sum(item.get('count', 0) for item in data.get('results', []))
        return total

    def about(self):
        messagebox.showinfo("关于", f"本程序仅供测试使用，联系开发者：411703730@qq.com")

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
        url = "https://api.fda.gov/device/event.json"
        search_query = self.format_search_query(self.generic_name.get(), self.query_type.get())
        
        params = {
            "search": search_query,
            "limit": min(int(self.limit.get()), 1000)  # 确保不超过1000
        }
        
        self.result_textbox.delete(1.0, "end")
        self.result_textbox.insert("end", f"查询类型: {self.query_type.get()}\n")
        self.result_textbox.insert("end", f"查询条件: {search_query}\n")
        self.result_textbox.insert("end", f"当前查询共有 {total_count} 条报告，正在查询个例...\n")
        self.root.update()
        
        data = self.make_api_request(url, params)
        if data is None:
            return
        
        results = data.get("results", [])
        
        # 显示前5条结果
        self.result_textbox.delete(1.0, "end")
        self.result_textbox.insert("end", f"查询类型: {self.query_type.get()}\n")
        self.result_textbox.insert("end", f"查询条件: {search_query}\n")
        self.result_textbox.insert("end", f"查询成功，返回{len(results)}条结果（共{total_count}条，显示前5条）：\n\n")
        
        display_count = min(5, len(results))
        for i in range(display_count):
            self.result_textbox.insert("end", f"=== 个例 {i+1} ===\n")
            # 显示设备信息以便比较
            device_info = results[i].get("device", [{}])[0] if isinstance(results[i].get("device"), list) else results[i].get("device", {})
            self.result_textbox.insert("end", f"设备通用名称: {device_info.get('generic_name', '')}\n")
            self.result_textbox.insert("end", f"设备名称: {device_info.get('device_name', '')}\n")
            self.result_textbox.insert("end", f"报告编号: {results[i].get('report_number', '')}\n\n")
        
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
                # 安全地获取设备信息
                device = result.get("device", [{}])[0] if isinstance(result.get("device"), list) else result.get("device", {})
                
                # 安全地获取患者信息
                patients = result.get("patient", [])
                patient = patients[0] if patients else {}
                
                # 安全地获取产品问题
                product_problems = result.get("product_problems", [])
                if isinstance(product_problems, list):
                    product_problems = ", ".join([str(p) for p in product_problems if p])
                else:
                    product_problems = str(product_problems)
                
                # 安全地获取患者问题
                patient_problems = patient.get("patient_problems", [])
                if isinstance(patient_problems, list):
                    patient_problems = ", ".join([str(p) for p in patient_problems if p])
                else:
                    patient_problems = str(patient_problems)
                
                # 安全地获取治疗信息
                treatments = patient.get("sequence_number_treatment", [])
                treatment = treatments[0] if treatments else ""
                
                simplified = {
                    "report_number": result.get("report_number", ""),
                    "type_of_report": ", ".join(result.get("type_of_report", [])) if isinstance(result.get("type_of_report"), list) else result.get("type_of_report", ""),
                    "event_type": result.get("event_type", ""),
                    "date_received": result.get("date_received", ""),
                    "date_of_event": result.get("date_of_event", ""),
                    "generic_name": device.get("generic_name", ""),
                    'mdr_text':result.get("mdr_text", ""),
                    "manufacturer_d_name": device.get("manufacturer_d_name", ""),
                    "product_problems": product_problems,
                    "patient_sequence_number": patient.get("patient_sequence_number", ""),
                    "patient_age": patient.get("patient_age", ""),
                    "patient_sex": patient.get("patient_sex", ""),
                    "patient_weight": patient.get("patient_weight", ""),
                    "patient_problems": patient_problems,
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
        search_query = self.format_search_query(self.generic_name.get(), self.query_type.get())
        
        # 定义汇总查询
        queries = [
            {
                "name": "事件类型统计",
                "url": "https://api.fda.gov/device/event.json",
                "params": {
                    "search": search_query,
                    "count": "event_type.exact"
                }
            },
            {
                "name": "产品问题统计",
                "url": "https://api.fda.gov/device/event.json",
                "params": {
                    "search": search_query,
                    "count": "product_problems.exact"     
                }
            },
            {
                "name": "伤害结果统计",
                "url": "https://api.fda.gov/device/event.json",
                "params": {
                    "search": f"{search_query} AND event_type:Injury",
                    "count": "patient.sequence_number_outcome.exact"
                }
            },
            {
                "name": "产品清单统计",
                "url": "https://api.fda.gov/device/event.json",
                "params": {
                    "search": search_query,
                    "count": "device.generic_name.exact",
                    "limit": 100  # 限制返回的产品数量
                }
            },
            {
                "name": "厂商统计",
                "url": "https://api.fda.gov/device/event.json",
                "params": {
                    "search": search_query,
                    "count": "device.manufacturer_d_name.exact",
                    "limit": 100  # 限制返回的厂商数量
                }
            }
        ]
        
        self.summary_results = {}
        
        self.result_textbox.insert("end", f"查询类型: {self.query_type.get()}\n")
        self.result_textbox.insert("end", f"查询条件: {search_query}\n")
        
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
                self.result_textbox.insert("end", f"  {term}: {count} \n")
            
            # 如果是产品清单或厂商统计，显示详细信息
            if query['name'] in ['产品清单统计', '厂商统计']:
                if count_data:
                    self.result_textbox.insert("end", f"共找到 {len(count_data)} 种{query['name'].replace('统计', '')}\n")
    
    def export_summary(self):
        if not hasattr(self, 'summary_results') or not self.summary_results:
            messagebox.showwarning("无数据", "没有可导出的汇总数据，请先执行查询")
            return
        
        try:
            # 创建DataFrame列表
            dfs = []
            
            for name, data in self.summary_results.items():
                count_data = data.get('results', [])
                if count_data:
                    df = pd.DataFrame(count_data)
                    df['统计类型'] = name
                    dfs.append(df)
            
            # 弹出保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
                title="保存汇总信息"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    if dfs:
                        # 按统计类型分组创建不同的工作表
                        for df in dfs:
                            # 清理工作表名称
                            sheet_name = df['统计类型'].iloc[0][:31].replace(':', '').replace('\\', '').replace('/', '').replace('?', '').replace('*', '').replace('[', '').replace(']', '')
                            # 移除统计类型列后保存
                            df_to_save = df.drop('统计类型', axis=1)
                            df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # 如果没有数据，创建一个空的工作表
                        pd.DataFrame().to_excel(writer, sheet_name='无数据', index=False)
                
                messagebox.showinfo("导出成功", f"汇总信息已成功导出到:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("导出错误", f"导出过程中出错: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = FDAQueryApp(root)
    root.mainloop()
