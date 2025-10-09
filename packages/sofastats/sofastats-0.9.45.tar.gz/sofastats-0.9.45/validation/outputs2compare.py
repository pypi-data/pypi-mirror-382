from webbrowser import open_new_tab

from sofastats.output.charts import area, bar, box_plot, histogram, line, pie, scatterplot
from sofastats.output.stats import (anova, chi_square, kruskal_wallis_h, mann_whitney_u, normality, pearsons_r,
    spearmans_r, ttest_indep, ttest_paired, wilcoxon_signed_ranks, )
from sofastats.output.tables import cross_tab, freq
from sofastats.output.tables.interfaces import Column, Row
from sofastats.output.utils import get_report

def anova_output():
    # anova.AnovaDesign(
    #     output_title='ANOVA SOFAStats',
    #     measure_field_name='height',
    #     grouping_field_name='sport',
    #     group_values=[1, 2, 3],
    #     style_name='prestige_screen',
    #     csv_file_path='sports.csv',
    #     high_precision_required=False,
    #     decimal_points=3,
    #     data_labels_yaml_file_path='var_labels.yaml',
    # ).make_output()
    anova.AnovaDesign(
        output_title='ANOVA SOFAStats',
        measure_field_name='Value',
        grouping_field_name='Group',
        group_values=[215, 366, 498, 649, 781, 932, ],
        style_name='prestige_screen',
        csv_file_path='/home/g/projects/sofastats/example_scripts/food_data_IN_LONG_FORMAT.csv',
    ).make_output()

def chi_square_output():
    chi_square.ChiSquareDesign(
        output_title='Chi Square Test',
        variable_a_name='book_type',
        variable_b_name='genre',
        csv_file_path='books.csv',
        decimal_points=3,
        show_workings=True,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def kruskal_wallis_h_output():
    kruskal_wallis_h.KruskalWallisHDesign(
        output_title="Kruskal-Wallis H Test",
        measure_field_name='height',
        grouping_field_name='sport',
        group_values=[1, 2, 3],
        csv_file_path='sports.csv',
        decimal_points=3,
        show_workings=True,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def mann_whitney_u_output():
    mann_whitney_u.MannWhitneyUDesign(
        output_title="Mann-Whitney U Test",
        measure_field_name='height',
        grouping_field_name='sport',
        group_a_value=1,
        group_b_value=2,
        csv_file_path='sports.csv',
        decimal_points=3,
        show_workings=True,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_item_output():
    ## Design first output item
    anova_design = anova.AnovaDesign(
        measure_field_name='height',
        grouping_field_name='sport',
        group_values=[1, 2, 3],
        style_name='prestige_screen',
        csv_file_path='sports.csv',
        overwrite_csv_derived_table_if_there=True,
        high_precision_required=False,
        decimal_points=3,
    )
    ## Design second output item
    kruskal_wallis_h_design = kruskal_wallis_h.KruskalWallisHDesign(
        measure_field_name='height',
        grouping_field_name='sport',
        group_values=[1, 2, 3],
        csv_file_path='sports.csv',
        overwrite_csv_derived_table_if_there=True,
        decimal_points=3,
        show_workings=True,
    )
    ## Combine items into list
    output_items = [anova_design, kruskal_wallis_h_design, ]
    ## Save your output file
    output_file_path = '/home/g/Documents/sofastats/reports/anova_vs_kruskal_wallis_h.html'
    get_report(output_items, title='First ever combined report').to_file(output_file_path)
    ## Open output in your default web browser
    open_new_tab(url=f"file://{output_file_path}")

def normality_one_measure_output():
    normality.NormalityDesign(
        output_title="Checking normality for one measure",
        variable_a_name='height',
        csv_file_path='sports.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def normality_two_measure_output():
    normality.NormalityDesign(
        output_title="Checking normality for two measures",
        variable_a_name='reading_score_before_help',
        variable_b_name='reading_score_after_help',
        csv_file_path='education.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def pearsons_r_output():
    pearsons_r.PearsonsRDesign(
        output_title="Pearson's R Correlation Test",
        variable_a_name='floor_area',
        variable_b_name='price',
        csv_file_path='properties.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def spearmans_r_output():
    spearmans_r.SpearmansRDesign(
        output_title="Spearman's R Correlation Test",
        variable_a_name='floor_area',
        variable_b_name='price',
        csv_file_path='properties.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def independent_t_test_output():
    ttest_indep.TTestIndepDesign(
        output_title="Independent Samples T-Test",
        measure_field_name='height',
        grouping_field_name='sport',
        group_a_value=1,
        group_b_value=2,
        csv_file_path='sports.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def paired_t_test_output():
    ttest_paired.TTestPairedDetails(
        output_title="Paired Samples T-Test",
        variable_a_name='reading_score_before_help',
        variable_b_name='reading_score_after_help',
        csv_file_path='education.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def wilcoxon_signed_ranks_output():
    wilcoxon_signed_ranks.WilcoxonSignedRanksDesign(
        output_title="Wilcoxon Signed Ranks Test",
        variable_a_name='school_satisfaction_before_help',
        variable_b_name='school_satisfaction_after_help',
        csv_file_path='education.csv',
        decimal_points=3,
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def area_chart_output():
    area.AreaChartDesign(
        output_title="Area Chart",
        category_field_name='age_group',
        chart_field_name='country',
        csv_file_path='people.csv',
        is_time_series=False,
        show_major_ticks_only=True,
        show_markers=True,
        rotate_x_labels=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Attendees',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def simple_bar_chart_output():
    bar.SimpleBarChartDesign(
        output_title="Simple Bar Chart",
        category_field_name='age_group',
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_bar_chart_output():
    bar.MultiBarChartDesign(
        output_title="Multi-Bar Chart",
        category_field_name='age_group',
        chart_field_name='country',
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def clustered_bar_chart_output():
    bar.ClusteredBarChartDesign(
        output_title="Clustered Bar Chart",
        category_field_name='age_group',
        series_field_name='country',
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_clustered_bar_chart_output():
    bar.MultiClusteredBarChartDesign(
        output_title="Multi-Clustered Bar Chart",
        chart_field_name='tertiary_qualifications',
        category_field_name='age_group',
        series_field_name='country',
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def box_plot_output():
    box_plot.BoxplotChartDesign(
        output_title="Box Plot",
        field_name='height',
        category_field_name='sport',
        csv_file_path='sports.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_series_box_plot_output():
    box_plot.MultiSeriesBoxplotChartDesign(
        output_title="Multi-Series Box Plot",
        field_name='height',
        category_field_name='sport',
        series_field_name='country',
        csv_file_path='sports.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def histogram_output():
    histogram.HistogramChartDesign(
        output_title="Histogram",
        field_name='height',
        csv_file_path='sports.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_chart_histogram_output():
    histogram.MultiChartHistogramChartDesign(
        output_title="Multi-Chart Histogram",
        field_name='height',
        chart_field_name='sport',
        csv_file_path='sports.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def line_chart_output():
    line.MultiLineChartDesign(
        output_title="Line Chart",
        category_field_name='age_group',
        series_field_name='country',
        csv_file_path='people.csv',
        is_time_series=False,
        show_major_ticks_only=True,
        show_markers=True,
        rotate_x_labels=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Attendees',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def simple_pie_chart_output():
    pie.PieChartDesign(
        output_title="Pie Chart",
        category_field_name='country',
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_chart_pie_chart_output():
    pie.MultiChartPieChartDesign(
        output_title="Multi-Chart Pie Chart",
        category_field_name='age_group',
        chart_field_name='country',
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def single_series_scatterplot_output():
    scatterplot.SingleSeriesScatterChartDetails(
        output_title="Single-Series Scatterplot",
        x_field_name='floor_area',
        y_field_name='price',
        csv_file_path='properties.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_series_scatterplot_output():
    scatterplot.MultiSeriesScatterChartDetails(
        output_title="Multi-Series Scatterplot",
        x_field_name='floor_area',
        y_field_name='price',
        series_field_name='valuer',
        csv_file_path='properties.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_chart_single_series_scatterplot_output():
    scatterplot.MultiChartScatterChartDetails(
        output_title="Multi-Chart Scatterplot",
        x_field_name='floor_area',
        y_field_name='price',
        chart_field_name='agency',
        csv_file_path='properties.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def multi_chart_multi_series_scatterplot_output():
    scatterplot.MultiChartSeriesScatterChartDetails(
        output_title="Multi-Chart Multi-Series Scatterplot",
        x_field_name='floor_area',
        y_field_name='price',
        series_field_name='valuer',
        chart_field_name='agency',
        csv_file_path='properties.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def cross_tab_output():
    cross_tab.CrossTabDesign(
        output_title="Cross-Tab Table",
        style_name='prestige_screen',
        rows = [
            Row(variable='country', has_total=True, sort_order='by increasing frequency'),
            # Row(variable='tertiary_qualifications'),
        ],
        columns=[
            Column(variable='age_group'),
        ],
        data_labels_yaml_file_path='var_labels.yaml',
        csv_file_path='people.csv',
    ).make_output()

def cross_tab_nested_output():
    design = cross_tab.CrossTabDesign(
        output_title="Nested Cross-Tab Table",
        rows = [
            Row(
                variable='country',
                has_total=True,
                sort_order='by increasing frequency',
            ),
            Row(
                variable='tertiary_qualifications',
                child=Row(
                    variable='handedness',
                )
            ),
        ],
        columns=[
            Column(variable='age_group'),
        ],
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def frequency_table_output():
    freq.FrequencyTableDesign(
        output_title="Frequency Table",
        rows = [
            Row(variable='country', has_total=True, sort_order='by increasing frequency'),
            Row(variable='tertiary_qualifications')],
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def frequency_table_nested_output():
    freq.FrequencyTableDesign(
        output_title="Nested Frequency Table",
        rows = [
            Row(
                variable='country',
                has_total=True,
                sort_order='by label',
                child=Row(
                    variable='tertiary_qualifications',
                ),
            ),
        ],
        csv_file_path='people.csv',
        data_labels_yaml_file_path='var_labels.yaml',
    ).make_output()

def run():
    pass
    anova_output()
    # chi_square_output()
    # kruskal_wallis_h_output()
    # mann_whitney_u_output()
    # multi_item_output()
    # normality_one_measure_output()
    # normality_two_measure_output()
    # pearsons_r_output()
    # spearmans_r_output()
    # independent_t_test_output()
    # paired_t_test_output()
    # wilcoxon_signed_ranks_output()
    # area_chart_output()
    # simple_bar_chart_output()
    # multi_bar_chart_output()
    # clustered_bar_chart_output()
    # multi_clustered_bar_chart_output()
    # box_plot_output()
    # multi_series_box_plot_output()
    # histogram_output()
    # multi_chart_histogram_output()
    # line_chart_output()
    # simple_pie_chart_output()
    # multi_chart_pie_chart_output()
    # single_series_scatterplot_output()
    # multi_series_scatterplot_output()
    # multi_chart_single_series_scatterplot_output()
    # multi_chart_multi_series_scatterplot_output()
    # cross_tab_output()
    # cross_tab_nested_output()
    # frequency_table_output()
    # frequency_table_nested_output()

if __name__ == '__main__':
    run()
