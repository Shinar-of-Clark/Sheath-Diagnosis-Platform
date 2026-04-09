import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import io
import base64
import os
import uuid

from ui_layout import get_text, app_layout
from algo_signal import process_sheath_data
from diagnostic_conclusions import evaluate_deviation, evaluate_dc, evaluate_thd, evaluate_ihd
from expert_system import run_expert_system

# --- Dash 应用 (使用 Bootstrap 主题) ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server # 暴露底层 Flask server 供生产级 WSGI 服务器（如 Gunicorn）调用
app.layout = app_layout

# --- 新增回调：更新所有文本内容 ---
@app.callback(
    [Output('language-select-label', 'children'),
     Output('main-title', 'children'),
     Output('input-params-header', 'children'),
     Output('freq-label', 'children'),
     Output('ppc-label', 'children'),
     Output('fs-label', 'children'),
     Output('upload-text-drag', 'children'),
     Output('upload-text-select', 'children'),
     Output('mock-generator-accordion-item', 'title'),
     Output('mock-rms-label', 'children'),
     Output('mock-freq-label', 'children'),
     Output('mock-ppc-label', 'children'),
     Output('mock-faults-label', 'children'),
     Output('mock-faults', 'options'), # 更新Checklist的options
     Output('mock-generate-button', 'children'),
     Output('filter-mode-radio', 'options'),
     Output('filter-config-label', 'children'),
     Output('filter-selector', 'options'), # 更新Checklist的options
     Output('advanced-thresholds-accordion-item', 'title'),
     Output('dc-threshold-label', 'children'),
     Output('dc-warn-label', 'children'),
     Output('dc-alarm-label', 'children'),
     Output('thd-threshold-label', 'children'),
     Output('thd-warn-label', 'children'),
     Output('thd-alarm-label', 'children'),
     Output('ihd-threshold-label', 'children'),
     Output('ihd-warn-label', 'children'),
     Output('ihd-alarm-label', 'children'),
     Output('deviation-threshold-label', 'children'),
     Output('dev-warn-label', 'children'),
     Output('dev-alarm-label', 'children'),
     Output('reset-thresholds-button', 'children'),
     Output('golden-cycle-header', 'children'),
     Output('harmonic-analysis-title', 'children'),
     Output('expert-system-header', 'children'),
     Output('changelog-accordion-item', 'title'),
     Output('changelog-content', 'children')],
    [Input('language-selector', 'value')]
)
def update_language(lang_code):
    # 更新 mock-faults options
    mock_fault_options = [
        {"label": get_text('mock_fault_noise', lang_code), "value": "noise"},
        {"label": get_text('mock_fault_dc', lang_code), "value": "dc"},
        {"label": get_text('mock_fault_h2', lang_code), "value": "h2"},
        {"label": get_text('mock_fault_h3', lang_code), "value": "h3"},
        {"label": get_text('mock_fault_h5', lang_code), "value": "h5"},
        {"label": get_text('mock_fault_h7', lang_code), "value": "h7"},
    ]

    # 更新 filter-mode-radio options
    filter_mode_options = [
        {"label": get_text('filter_mode_custom', lang_code), "value": "custom"},
        {"label": get_text('filter_mode_auto', lang_code), "value": "auto"},
    ]

    # 更新 filter-selector options
    filter_selector_options = [
        {"label": get_text('filter_dc_removal', lang_code), "value": "dc_removal_raw"},
        {"label": f"{get_text('filter_butterworth', lang_code)}{get_text('filter_butterworth_hint', lang_code)}", "value": "butter"},
        {"label": get_text('filter_comb', lang_code), "value": "comb"},
        {"label": get_text('filter_ema', lang_code), "value": "ema"},
    ]

    # 更新 Changelog Markdown 内容
    changelog_markdown_content = f'''
### {get_text('update_log_v2_title', lang_code)}
{get_text('update_log_v2_desc', lang_code)}

**{get_text('fault_matrix_title', lang_code)}**
| {get_text('fault_category_col', lang_code)} | {get_text('primary_feature_col', lang_code)} | {get_text('secondary_feature_col', lang_code)} | {get_text('monitoring_function_col', lang_code)} |
| :--- | :--- | :--- | :--- |
| **{get_text('fault_cross_bonding', lang_code)}** | {get_text('fault_cross_bonding_primary', lang_code)} | {get_text('fault_cross_bonding_secondary', lang_code)} | {get_text('fault_cross_bonding_monitor', lang_code)} |
| **{get_text('fault_open_circuit', lang_code)}** | {get_text('fault_open_circuit_primary', lang_code)} | {get_text('fault_open_circuit_secondary', lang_code)} | {get_text('fault_open_circuit_monitor', lang_code)} |
| **{get_text('fault_multi_grounding', lang_code)}** | {get_text('fault_multi_grounding_primary', lang_code)} | {get_text('fault_multi_grounding_secondary', lang_code)} | {get_text('fault_multi_grounding_monitor', lang_code)} |
| **{get_text('fault_water_ingress', lang_code)}** | {get_text('fault_water_ingress_primary', lang_code)} | {get_text('fault_water_ingress_secondary', lang_code)} | {get_text('fault_water_ingress_monitor', lang_code)} |
| **{get_text('fault_loose_contact', lang_code)}** | {get_text('fault_loose_contact_primary', lang_code)} | {get_text('fault_loose_contact_secondary', lang_code)} | {get_text('fault_loose_contact_monitor', lang_code)} |

---

### {get_text('update_log_v1_title', lang_code)}
{get_text('update_log_v1_desc', lang_code)}

**1. {get_text('v1_feature_1_title', lang_code)}**
{get_text('v1_feature_1_items', lang_code)}

**2. {get_text('v1_feature_2_title', lang_code)}**
{get_text('v1_feature_2_items', lang_code)}
    '''

    return [
        get_text('language_select_label', lang_code),
        get_text('title', lang_code),
        get_text('input_params_header', lang_code),
        get_text('freq_label', lang_code),
        get_text('ppc_label', lang_code),
        get_text('fs_label', lang_code),
        get_text('upload_text_drag', lang_code),
        get_text('upload_text_select', lang_code),
        f"{get_text('mock_generator_title', lang_code)} 🌟New",
        get_text('mock_rms_label', lang_code),
        get_text('mock_freq_label', lang_code),
        get_text('mock_ppc_label', lang_code),
        get_text('mock_faults_label', lang_code),
        mock_fault_options,
        get_text('mock_generate_button', lang_code),
        filter_mode_options,
        get_text('filter_config_label', lang_code),
        filter_selector_options,
        get_text('advanced_thresholds_title', lang_code),
        get_text('dc_threshold_label', lang_code),
        get_text('warn_label', lang_code),
        get_text('alarm_label', lang_code),
        get_text('thd_threshold_label', lang_code),
        get_text('warn_label', lang_code),
        get_text('alarm_label', lang_code),
        get_text('ihd_threshold_label', lang_code),
        get_text('warn_label', lang_code),
        get_text('alarm_label', lang_code),
        get_text('deviation_threshold_label', lang_code),
        get_text('warn_label', lang_code),
        get_text('alarm_label', lang_code),
        get_text('reset_thresholds_button', lang_code),
        get_text('golden_cycle_header', lang_code),
        get_text('harmonic_analysis_header', lang_code),
        get_text('expert_system_header', lang_code),
        get_text('update_log_title', lang_code),
        changelog_markdown_content
    ]

# --- 回调1：当上传新数据或修改频率时，在后台静默计算最佳组合并存入 Store ---
@app.callback(
    Output('best-filter-store', 'data'),
    [Input('upload-data', 'contents'), Input('input-freq', 'value'), Input('input-ppc', 'value')]
)
def update_best_filters(contents, freq, ppc):
    if not contents:
        return dash.no_update

    try:
        content_string = contents.split(',')[1]
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        raw_values = df.iloc[:, 0].values
        fs = freq * ppc

        candidates = [
            ["dc_removal_raw", "butter"],
            ["dc_removal_raw", "comb"],
            ["dc_removal_raw", "ema"],
            ["dc_removal_raw"],
            [],
            ["dc_removal_raw", "butter", "comb", "ema"] # 新增：所有滤波器组合
        ]
        best_filters = []
        # 修正：最佳组合应选择使“滤波后(真实) RMS”最小的组合，这表示移除了最多的干扰。
        min_processed_rms = float('inf') 

        for combo in candidates:
            try: # 增加异常处理，避免某个滤波器在特定数据上报错中断寻优
                res = process_sheath_data(raw_values, fs=fs, freq=freq, selected_filters=combo)
                current_processed_rms = res['rms']
                # 寻找使处理后 RMS 最小的组合
                if current_processed_rms < min_processed_rms:
                    min_processed_rms = current_processed_rms
                    best_filters = combo
            except Exception:
                continue
        
        # 如果没有找到任何有效的最佳组合（例如所有组合都报错），则返回默认值
        if not best_filters:
            return ["dc_removal_raw", "butter"] # Default to pre-processing + butterworth
        return best_filters
    except Exception:
        return dash.no_update

# --- 回调2：处理单选框与复选框的智能双向联动 ---
@app.callback(
    [Output('filter-selector', 'value'), Output('filter-mode-radio', 'value')],
    [Input('filter-mode-radio', 'value'), Input('filter-selector', 'value'), Input('best-filter-store', 'data')],
    prevent_initial_call=True
)
def sync_filter_mode(mode, selected_filters, best_filters):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # 如果触发的是单选框选择了“自动”，或后台算出了新的最佳组合
    if trigger_id in ['filter-mode-radio', 'best-filter-store']:
        if mode == 'auto' and best_filters is not None:
            return best_filters, dash.no_update # 勾选最佳组合

    # 如果用户手动点了下面的复选框
    elif trigger_id == 'filter-selector':
        if mode == 'auto' and best_filters is not None:
            if set(selected_filters or []) != set(best_filters):
                return dash.no_update, 'custom' # 不匹配说明是手动修改，单选框跳回“自定义”

    return dash.no_update, dash.no_update

# --- 新增回调：实时计算并显示采样频率 (fs) ---
@app.callback(
    Output('calculated-fs-value', 'children'),
    [Input('input-freq', 'value'), Input('input-ppc', 'value')]
)
def update_fs_display(freq, ppc):
    if freq is not None and ppc is not None:
        return f"{freq * ppc}"
    return "N/A"

# --- 新增回调：重置高级阈值 ---
@app.callback(
    [Output("thr-dc-warn", "value"), Output("thr-dc-alarm", "value"),
     Output("thr-thd-warn", "value"), Output("thr-thd-alarm", "value"),
     Output("thr-ihd-warn", "value"), Output("thr-ihd-alarm", "value"),
     Output("thr-dev-warn", "value"), Output("thr-dev-alarm", "value")], # 新增干扰偏差率的输出
    [Input("reset-thresholds-button", "n_clicks")],
    prevent_initial_call=True
)
def reset_thresholds(n_clicks):
    # 返回所有默认值
    return 0.1, 0.2, \
           8.0, 15.0, \
           5.0, 10.0, \
           5.0, 10.0 # 干扰偏差率的默认值

@app.callback(
    [Output('main-plot', 'figure'), Output('metrics-output', 'children'), 
     Output('h-table', 'data'), Output('h-table', 'columns'),
     Output('error-msg', 'children'), Output('error-msg', 'is_open'), # 错误信息保持不变
     Output('thd-display', 'children'),
     Output('harmonic-diagnosis-output', 'children'),
     Output('expert-system-output', 'children')],
    [Input('upload-data', 'contents'), Input('filter-selector', 'value'), 
     Input('input-freq', 'value'), Input('input-ppc', 'value'),
     Input('thr-dc-warn', 'value'), Input('thr-dc-alarm', 'value'), # 接收新的动态阈值输入
     Input('thr-thd-warn', 'value'), Input('thr-thd-alarm', 'value'),
     Input('thr-ihd-warn', 'value'), Input('thr-ihd-alarm', 'value'),
     Input('thr-dev-warn', 'value'), Input('thr-dev-alarm', 'value'),
     Input('language-selector', 'value')], # 监听语言切换以实时重新生成诊断结论
    [State('upload-data', 'filename')]
)
def update(contents, selected_filters, freq, ppc, thr_dc_warn, thr_dc_alarm, thr_thd_warn, thr_thd_alarm, thr_ihd_warn, thr_ihd_alarm, thr_dev_warn, thr_dev_alarm, lang_code, filename):
    # 终极防御：为动态容器分配每次都独一无二的 key，强制 React 销毁重建而非比对复用，彻底杜绝 removeChild 报错
    uid = str(uuid.uuid4())
    
    if not contents: return go.Figure(), html.Div(key=uid), [], [], "", False, "", html.Div(key=uid), html.Div(key=uid)
    try:
        # 防空保护：如果用户把输入框清空了，自动使用默认值兜底
        thr_dc_warn = thr_dc_warn if thr_dc_warn is not None else 0.1
        thr_dc_alarm = thr_dc_alarm if thr_dc_alarm is not None else 0.2
        thr_thd_warn = thr_thd_warn if thr_thd_warn is not None else 8.0
        thr_thd_alarm = thr_thd_alarm if thr_thd_alarm is not None else 15.0
        thr_ihd_warn = thr_ihd_warn if thr_ihd_warn is not None else 5.0
        thr_ihd_alarm = thr_ihd_alarm if thr_ihd_alarm is not None else 10.0
        thr_dev_warn = thr_dev_warn if thr_dev_warn is not None else 5.0 # 干扰偏差率的默认值
        thr_dev_alarm = thr_dev_alarm if thr_dev_alarm is not None else 10.0 # 干扰偏差率的默认值

        fs = freq * ppc # 仍然需要fs用于 process_sheath_data
        content_string = contents.split(',')[1]
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        # 修正：移除重复调用，并确保传递 freq 参数
        res = process_sheath_data(df.iloc[:, 0].values, fs=fs, freq=freq, selected_filters=selected_filters) # 修正：这里不再需要传入 thr 参数

        fig = go.Figure(data=[go.Scatter(y=res['golden_cycle'], line=dict(color='#e74c3c', width=3))])
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)

        # 计算干扰偏差率
        clean_rms = res['rms']
        raw_rms = res['raw_rms']
        diff_pct = abs(raw_rms - clean_rms) / clean_rms * 100 if clean_rms > 0 else 0.0
        
        badge_text, badge_color, dev_diagnosis = evaluate_deviation(diff_pct, thr_dev_warn, thr_dev_alarm, lang_code)
        metrics_badge = dbc.Badge(badge_text, color=badge_color, className="ms-2")

        dc_offset_val = res['dc']
        dc_badge, dc_diagnosis = evaluate_dc(dc_offset_val, thr_dc_warn, thr_dc_alarm, lang_code)

        metrics = [
            html.Div([html.Span(get_text('raw_rms_label', lang_code), className="fw-bold text-muted"), html.Span(f"{raw_rms:.4f} A")], className="mb-1"),
            html.Div([html.Span(get_text('clean_rms_label', lang_code), className="fw-bold text-primary"), html.Span(f"{clean_rms} A")], className="mb-1"),
            html.Div([html.Span(get_text('deviation_rate_label', lang_code), className="fw-bold"), html.Span(f"{diff_pct:.2f}%"), metrics_badge], className="mb-3 mt-2 border-bottom pb-2"),
            html.Div([html.P(d, className="mb-0 text-danger small") for d in dev_diagnosis], className="mt-2"),
            html.Div([html.Span(get_text('dc_offset_label', lang_code), className="fw-bold"), html.Span(f"{dc_offset_val} A"), dc_badge], className="mb-1"),
            html.Div([html.P(d, className="mb-0 text-danger small") for d in dc_diagnosis], className="mt-2")
        ]
        
        cols = [
            {"name": get_text('harmonic_feature_col', lang_code), "id": "特征"},
            {"name": get_text('harmonic_amplitude_col', lang_code), "id": "幅值(A)"},
            {"name": get_text('harmonic_phase_col', lang_code), "id": "相位(°)"},
            {"name": get_text('harmonic_relative_col', lang_code), "id": "相对基波(%)"}
        ]

        thd_val = res['thd']
        thd_badge, thd_diagnosis = evaluate_thd(thd_val, thr_thd_warn, thr_thd_alarm, lang_code)
        ihd_badge, ihd_diagnosis = evaluate_ihd(res['harmonics'], thr_ihd_warn, thr_ihd_alarm, lang_code)

        harmonic_diagnosis_output_children = [
            html.Div([html.Span(f"{get_text('thd_label', lang_code)} ", className="fw-bold"), thd_badge], className="mb-1 mt-3 border-top pt-2"),
            html.Div([html.P(d, className="mb-0 text-danger small") for d in thd_diagnosis], className="mt-2"),
            html.Div([html.Span(f"{get_text('harmonic_analysis_header', lang_code)} (IHD): ", className="fw-bold"), ihd_badge], className="mb-1 mt-3 border-top pt-2"),
            html.Div([html.P(d, className="mb-0 text-danger small") for d in ihd_diagnosis], className="mt-2")
        ]

        expert_diagnosis_children = run_expert_system(clean_rms, dc_offset_val, res['harmonics'], thr_dc_alarm, thr_ihd_alarm, lang_code)

        # 动态翻译表格里的谐波特征名称 (保证不污染底层分析算法)
        display_harmonics = []
        harmonic_name_map = {"1次谐波": "1st Harmonic", "2次谐波": "2nd Harmonic", "3次谐波": "3rd Harmonic", "5次谐波": "5th Harmonic", "7次谐波": "7th Harmonic"}
        for h in res['harmonics']:
            h_copy = dict(h)
            if lang_code == 'en':
                h_copy["特征"] = harmonic_name_map.get(h["特征"], h["特征"])
            display_harmonics.append(h_copy)

        return fig, html.Div(metrics, key=uid), display_harmonics, cols, "", False, \
               f"{get_text('thd_label', lang_code)} {res['thd']:.2f}%", html.Div(harmonic_diagnosis_output_children, key=uid), html.Div(expert_diagnosis_children, key=uid)
    except Exception as e:
        return go.Figure(), html.Div(key=uid), [], [], f"{get_text('error_prefix', lang_code)}{str(e)}", True, "", html.Div(key=uid), html.Div(key=uid)

# --- 新增回调：自定义组合故障波形生成 ---
@app.callback(
    Output("download-custom-mock", "data"),
    [Input("mock-generate-button", "n_clicks")],
    [State("mock-rms", "value"),
     State("mock-freq", "value"),
     State("mock-ppc", "value"),
     State("mock-faults", "value")],
    prevent_initial_call=True
)
def generate_custom_mock(n_clicks, rms, freq, ppc, faults):
    # 容错：防止用户输入空值，以及限制后台最高采样点
    if rms is None or rms <= 0: rms = 10.0
    if freq is None or freq <= 0: freq = 50
    if ppc is None or ppc > 256: ppc = 256  # 强制限制，防止后台因庞大数组崩溃
    
    fs = freq * ppc
    duration = 1.0  # 自动生成 1 秒钟的数据
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    A1 = rms * np.sqrt(2) # 基波峰值
    signal = A1 * np.sin(2 * np.pi * freq * t)
    
    if faults:
        if "noise" in faults: signal += np.random.normal(0, A1 * 0.5, len(t)) # 增加噪声能量，以突破 >10% 的偏差率报警阈值
        if "dc" in faults: signal += 0.5  # 加入 0.5A 恒定直流
        if "h2" in faults: signal += A1 * 0.12 * np.sin(2 * np.pi * 2 * freq * t + 0.1) # 12% 2次谐波
        if "h3" in faults: signal += A1 * 0.15 * np.sin(2 * np.pi * 3 * freq * t + 0.3) # 15% 3次谐波
        if "h5" in faults: signal += A1 * 0.12 * np.sin(2 * np.pi * 5 * freq * t + 0.5) # 12% 5次谐波
        if "h7" in faults: signal += A1 * 0.11 * np.sin(2 * np.pi * 7 * freq * t + 0.7) # 11% 7次谐波
        
    df = pd.DataFrame({"current": signal.astype(np.float32)})
    return dcc.send_data_frame(df.to_csv, "custom_fault_mock.csv", index=False)

if __name__ == '__main__':
    # 开启 debug 和热重载(hot_reload)，修改 python 代码或页面控件都会实时刷新
    app.run(debug=True, port=8051, dev_tools_hot_reload=True)