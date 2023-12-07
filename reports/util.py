import pandas as pd
import seaborn as sns

# Apply the default theme
sns.set_theme()


class PerfTestReport:
    def __init__(self, result_path):
        raw = pd.read_json(result_path).set_index('test')
        self.timings = raw.timings.explode().to_frame().reset_index()

    def boxplot(self):
        return sns.boxplot(self.timings, x='timings', y='test')

    def violinplot(self):
        return sns.violinplot(self.timings, x='timings', y='test')

    def stripplot(self):
        return sns.stripplot(self.timings, x='timings', y='test')

    def swarmplot(self):
        return sns.swarmplot(self.timings, x='timings', y='test')
