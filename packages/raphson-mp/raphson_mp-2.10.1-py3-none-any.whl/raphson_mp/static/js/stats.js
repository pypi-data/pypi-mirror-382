/*
Build eCharts on this page: https://echarts.apache.org/en/builder.html
Charts: Bar, Heatmap
Coordinate systems: Grid
Component: Title, Legend, Tooltip, VisualMap
Others: Code Compression

https://echarts.apache.org/en/builder/echarts.html?charts=bar,heatmap&components=gridSimple,title,legendScroll,tooltip,visualMap
*/
import "../lib/echarts-6.0.0.js";
import { checkResponseCode, throttle, vars } from "./util.js";

// https://echarts.apache.org/en/option.html
const commonOptions = {
    backgroundColor: 'transparent',
    textStyle: {
        fontFamily: 'Quicksand',
    },
    color: [
        '#dd6b66',
        '#759aa0',
        '#e69d87',
        '#8dc1a9',
        '#ea7e53',
        '#eedd78',
        '#73a373',
        '#73b9bc',
        '#7289ab',
        '#91ca8c',
        '#f49f42',
        '#a77fdd',
        '#dd7f98',
        '#ddab7f',
        '#7f91dd',
    ],
    animationDuration: 500,
    tooltip: {
        backgroundColor: 'rgba(50,50,50,0.9)',
    },
    grid: {
        left: 0,
        right: 200, // legend
        bottom: 0,
        top: 60, // title
    },
};

const BUTTONS_CONTAINER = /** @type {HTMLDivElement} */ (document.getElementById('buttons'));

/**
 *
 * @param {HTMLButtonElement} button
 * @param {string} period
 */
async function loadCharts(button, period) {
    console.info('load charts:', period);

    // Update buttons
    for (const otherButton of BUTTONS_CONTAINER.children) {
        if (otherButton instanceof HTMLButtonElement) {
            otherButton.disabled = false;
        }
    }
    button.disabled = true;

    // Render charts
    for (const chartElem of document.getElementsByClassName("chart")) {
        if (!(chartElem instanceof HTMLElement)) continue;
        const id = chartElem.dataset.id;
        // run async code without waiting
        (async () => {
            const response = await fetch('/stats/data/' + encodeURIComponent(id) + '?period=' + encodeURIComponent(period), {});
            if (response.status == 200) {
                chartElem.hidden = false;
                const data = await response.json();
                chartElem.style.border = '';
                let eChart = echarts.getInstanceByDom(chartElem);
                if (!eChart) {
                    eChart = echarts.init(chartElem, 'dark');
                }
                // https://echarts.apache.org/en/api.html#echartsInstance.setOption
                // replaceMerge is required to be able to remove data (e.g. when going from last year to last week's data)
                eChart.setOption({...data, ...commonOptions}, {replaceMerge: ['series'], lazyUpdate: true});
            } else if (response.status == 204) {
                chartElem.hidden = true;
                echarts.dispose(chartElem);
            } else {
                checkResponseCode(response);
            }
        })();
    }
}

if (window.location.hash == "") {
    window.location.hash = "week"
}

for (const button of BUTTONS_CONTAINER.children) {
    if (!(button instanceof HTMLButtonElement)) continue;

    const period = /** @type {string} */ (button.dataset.period);

    button.addEventListener('click', () => {
        window.location.hash = period;
        loadCharts(button, period);
    });

    if (window.location.hash == '#' + period) {
        loadCharts(button, period);
    }
}

// Resize charts with page
{
    const resize = throttle(100, true, () => {
        for (const chartElem of document.getElementsByClassName("chart")) {
            let eChart = echarts.getInstanceByDom(chartElem);
            if (eChart) {
                // https://echarts.apache.org/en/api.html#echartsInstance.resize
                eChart.resize({animation: {duration: 50}});
            }
        }
    });
    window.addEventListener('resize', resize);
}

// Buttons background color
{
    const headingRect = document.getElementsByClassName('page-heading')[0].getBoundingClientRect();
    const buttonsY = headingRect.y + headingRect.height;

    function setButtonsBackground() {
        BUTTONS_CONTAINER.classList.toggle('background', window.scrollY > buttonsY);
    }

    window.addEventListener('scroll', setButtonsBackground);
    setButtonsBackground();
}
