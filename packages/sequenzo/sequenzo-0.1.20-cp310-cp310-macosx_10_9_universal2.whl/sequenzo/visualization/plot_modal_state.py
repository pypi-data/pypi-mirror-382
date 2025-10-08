"""
@Author  : Yuqi Liang 梁彧祺
@File    : plot_modal_state.py
@Time    : 01/03/2025 13:45
@Desc    : 
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Union, List
from sequenzo import SequenceData
from sequenzo.visualization.utils import (
    set_up_time_labels_for_x_axis,
    create_standalone_legend,
    save_figure_to_buffer,
    combine_plot_with_legend,
    save_and_show_results,
    show_plot_title
)
from PIL import Image


def plot_modal_state(seqdata: SequenceData,
                     group_by: Optional[Union[str, pd.Series, np.ndarray]] = None,
                     group_labels: Optional[List[str]] = None,
                     weights="auto",
                     xlabel: str = "Time",
                     ylabel: str = "Rel. Freq.",
                     fig_width: int = 12,
                     fig_height: Optional[int] = None,
                     show_counts: bool = True,
                     show_group_titles: bool = True,
                     fontsize: int = 12,
                     save_as: Optional[str] = None,
                     dpi: int = 200) -> None:
    """
    Creates a modal state frequency plot showing the most frequent state at each position
    and its relative frequency, with optional grouping by a categorical variable.

    :param seqdata: SequenceData object containing sequence information
    :param group_by: Column name or array with grouping variable
    :param group_labels: Optional custom labels for groups
    :param weights: (np.ndarray or "auto") Weights for sequences. If "auto", uses seqdata.weights if available
    :param xlabel: Label for the x-axis
    :param ylabel: Label for the y-axis
    :param fig_width: Width of the figure
    :param fig_height: Height of the figure (auto-calculated based on groups if None)
    :param show_counts: Whether to show the count of sequences in each group title
    :param save_as: Optional file path to save the plot
    :param dpi: Resolution of the saved plot

    :return: None
    """
    # Process weights
    if isinstance(weights, str) and weights == "auto":
        weights = getattr(seqdata, "weights", None)
    
    if weights is not None:
        weights = np.asarray(weights, dtype=float).reshape(-1)
        if len(weights) != len(seqdata.values):
            raise ValueError("Length of weights must equal number of sequences.")
    
    # Get sequence data as a DataFrame
    seq_df = seqdata.to_dataframe()

    # Ensure seq_df has the same index as the original data
    # This is crucial to align the grouping variable with sequence data
    seq_df.index = seqdata.data.index
    
    # Get weights for all sequences
    if weights is None:
        w_all = np.ones(len(seq_df))
    else:
        w_all = np.asarray(weights)

    # Create state mapping from numerical values back to state names
    inv_state_mapping = {v: k for k, v in seqdata.state_mapping.items()}

    # Process grouping variable
    if group_by is None:
        # If no grouping, create a single group with all sequences
        groups = pd.Series(["All Sequences"] * len(seq_df), index=seq_df.index)
        if group_labels is None:
            group_labels = ["All Sequences"]
    elif isinstance(group_by, str):
        # If grouping by column name from original data
        if group_by not in seqdata.data.columns:
            raise ValueError(f"Column '{group_by}' not found in sequence data")
        groups = seqdata.data[group_by]
        if group_labels is None:
            group_labels = sorted(groups.unique())
    else:
        # If grouping by external array or Series
        if len(group_by) != len(seq_df):
            raise ValueError("Length of group_by must match number of sequences")
        groups = pd.Series(group_by)
        if group_labels is None:
            group_labels = sorted(set(groups))

    # Prepare plotting
    n_groups = len(group_labels)
    n_time_points = len(seq_df.columns)

    if fig_height is None:
        # Auto-calculate height based on number of groups
        fig_height = max(4, 3 * n_groups)

    # TODO: Title is not very pretty here so I decided to remove it.
    # But here I keep 1 to keep the space big enough for the distance
    # between the second subplot and the upper first subplot
    title_height = 1
    adjusted_fig_height = fig_height + title_height

    # Create main figure with additional space for title
    main_fig = plt.figure(figsize=(fig_width, adjusted_fig_height))

    # No title, use whole figure for plots
    plot_gs = main_fig.add_gridspec(nrows=n_groups, height_ratios=[1] * n_groups, hspace=0.3)

    # Create axes for each group
    axes = []
    for i in range(n_groups):
        axes.append(main_fig.add_subplot(plot_gs[i]))

    # Make sure all axes share x and y scales
    for ax in axes[1:]:
        ax.sharex(axes[0])
        ax.sharey(axes[0])

    # Get colors for states
    colors = seqdata.color_map_by_label

    # Process each group
    for i, group in enumerate(group_labels):
        ax = axes[i]

        # Get indices for this group
        group_indices = groups == group
        group_count = group_indices.sum()

        # Skip if no sequences in this group
        if group_count == 0:
            continue

        # Subset data for this group and get corresponding weights
        group_data = seq_df[group_indices]
        w = w_all[group_indices.to_numpy()]

        # Calculate modal states and their frequencies for each time point
        modal_states = []
        modal_freqs = []

        for col in group_data.columns:
            states_idx = group_data[col].to_numpy()
            
            # Calculate weighted counts for each state
            weighted_sum = {}
            # Use numerical state indices (1, 2, 3, ...) instead of state labels
            for s_num in range(1, len(seqdata.states) + 1):  # s_num is the integer encoding
                weighted_sum[s_num] = float(w[states_idx == s_num].sum())
            
            totw = float(w.sum())
            
            if totw > 0:
                # Find the state with maximum weighted count
                modal_s = max(weighted_sum, key=weighted_sum.get)
                modal_state = inv_state_mapping[modal_s]
                modal_freq = weighted_sum[modal_s] / totw
            else:
                modal_state, modal_freq = None, 0.0
            
            modal_states.append(modal_state)
            modal_freqs.append(modal_freq)

        # Equal width for all bars
        x = np.arange(n_time_points)
        bar_width = 0.8  # Fixed width for all bars

        # Create bars with consistent width
        for j, (state, freq) in enumerate(zip(modal_states, modal_freqs)):
            if state is not None:
                # state is already a label from inv_state_mapping
                ax.bar(x[j], freq, width=bar_width, color=colors[state],
                       edgecolor='white', linewidth=0.5)

        # Set group title with count if requested
        if show_group_titles:
            if show_counts:
                if weights is not None and not np.allclose(weights, 1.0):
                    sum_w = float(w.sum())
                    title_text = f"{group} (n={group_count}, total weight={sum_w:.1f})"
                else:
                    title_text = f"{group} (n={group_count})"
            else:
                title_text = group
            show_plot_title(ax, title_text, show=True, fontsize=fontsize, pad=15)

        # Set y-axis limits and ticks
        ax.set_ylim(0, 1.0)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])

        # Set grid and spines
        ax.grid(axis='y', color='#E0E0E0', linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)

        # Clean up borders
        for spine in ax.spines.values():
            spine.set_color('#CCCCCC')
            spine.set_linewidth(0.5)

        # Add y-label only for the middle subplot
        if i == n_groups // 2:
            ax.set_ylabel(ylabel, fontsize=fontsize)

    # Set up X-axis (time) labels on the bottom subplot
    set_up_time_labels_for_x_axis(seqdata, axes[-1])
    axes[-1].set_xlabel(xlabel, fontsize=fontsize, labelpad=10)

    # Save main figure to memory
    main_buffer = save_figure_to_buffer(main_fig, dpi=dpi)

    # Create a legend
    # Create standalone legend
    legend_buffer = create_standalone_legend(
        colors=colors,
        labels=seqdata.labels,
        ncol=min(5, len(seqdata.states)),
        figsize=(fig_width, 1),
        fontsize=fontsize-2,
        dpi=dpi
    )

    if save_as and not save_as.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        save_as = save_as + '.png'

    # Combine main plot with legend
    combined_img = combine_plot_with_legend(
        main_buffer,
        legend_buffer,
        output_path=save_as,
        dpi=dpi,
        padding=20  # Increased padding between plot and legend
    )

    # Display combined image
    plt.figure(figsize=(fig_width, adjusted_fig_height + 1))
    plt.imshow(combined_img)
    plt.axis('off')
    plt.show()
    plt.close()



if __name__ == '__main__':
    # Import necessary libraries
    from sequenzo import *  # Social sequence analysis
    import pandas as pd  # Data manipulation

    # List all the available datasets in Sequenzo
    print('Available datasets in Sequenzo: ', list_datasets())

    # Load the data that we would like to explore in this tutorial
    # `df` is the short for `dataframe`, which is a common variable name for a dataset
    df = load_dataset('country_co2_emissions')

    # Create a SequenceData object from the dataset

    # Define the time-span variable
    time = list(df.columns)[1:]

    states = ['Very Low', 'Low', 'Middle', 'High', 'Very High']

    sequence_data = SequenceData(df, time=time, time_type="year", id_col="country", states=states)

    plot_modal_state(sequence_data)

