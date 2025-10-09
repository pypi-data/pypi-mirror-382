<script lang="ts">
    /**
     * Props for the ScrollEffect component.
     * @typedef {Object} Props
     * @property {Array<{title: string, name: string}>} credits - List of credits with title and name.
     * @property {number} speed - Animation speed in seconds.
     * @property {number} base_font_size - Base font size in rem (default: 1.5).
     * @property {string | null} background_color - Background color (default: black).
     * @property {string | null} title_color - Title text color (default: white).
     * @property {string | null} scroll_section_title_color - Section title color.
     * @property {string | null} name_color - Name text color (default: white).
     * @property {string | null} intro_title - Optional intro title.
     * @property {string | null} intro_subtitle - Optional intro subtitle.
     * @property {"stacked" | "two-column"} layout_style - Layout for credits.
     * @property {boolean} title_uppercase - Transform title to uppercase.
     * @property {boolean} name_uppercase - Transform name to uppercase.
     * @property {boolean} section_title_uppercase - Transform section title to uppercase.
     * @property {boolean} swap_font_sizes_on_two_column - Swap title/name font sizes.
     * @property {{path: string | null, url: string | null, ...} | null} scroll_logo_path - Logo to display inside the scroll.
     * @property {string} scroll_logo_height - Height of the scrolling logo.
     * 
     */
    export let credits: Props['credits'];
    export let speed: number;
    export let base_font_size: number = 1.5;
    export let background_color: string | null = null;
    export let title_color: string | null = null;
    export let scroll_section_title_color: string | null = null;
    export let name_color: string | null = null;
    export let intro_title: string | null = null;
    export let intro_subtitle: string | null = null;
    export let layout_style: "stacked" | "two-column" = "stacked";
    export let title_uppercase: boolean = false;
    export let name_uppercase: boolean = false;
    export let section_title_uppercase: boolean = true;
    export let swap_font_sizes_on_two_column: boolean = false;
    export let scroll_logo_path: { url: string | null } | null = null;
    export let scroll_logo_height: string = "120px";

    // Flag to trigger animation reset
    let reset = false;

    // Combine intro and credits for display
    $: display_items = (() => {
        const items = [];
        if (intro_title || intro_subtitle) {
            items.push({ 
                title: intro_title || '', 
                name: intro_subtitle || '',
                is_intro: true
            });
        }
        return [...items, ...credits.map(c => ({ ...c, is_intro: false }))];
    })();

    // Reactive styles for title and name
    $: title_style = (is_intro: boolean) => `color: ${title_color || 'white'}; font-size: ${is_intro ? base_font_size * 1.5 : base_font_size}rem;`;
    $: name_style = (is_intro: boolean) => `color: ${name_color || 'white'}; font-size: ${is_intro ? base_font_size * 0.9 : base_font_size * 0.8}rem;`;    
    $: section_title_style = `color: ${scroll_section_title_color || title_color || 'white'}; font-size: ${base_font_size * 1.2}rem;`;
    
    // Reset animation on prop changes
   function resetAnimation() {
        reset = true;
        setTimeout(() => (reset = false), 0);
    }

    // Trigger reset on prop changes
    $: credits, speed, resetAnimation();
</script>

<div class="wrapper" style:--animation-duration="{speed}s" style:background={background_color || 'black'}>
    {#if !reset}
        <div class="credits-container">
            {#if scroll_logo_path?.url}
                <div class="scroll-logo-container" style:height={scroll_logo_height}>
                <img src={scroll_logo_path.url} alt="Scrolling Logo" style:height={scroll_logo_height} />
                </div>
            {/if}
            {#each display_items as item}
                <!-- Render Section Title -->
                {#if item.section_title}
                    <div class="section-title" style={section_title_style} class:uppercase={section_title_uppercase}>
                        {item.section_title}
                    </div>

                <!-- Render Credit or Intro -->
                {:else}
                    {#if layout_style === 'two-column' && !item.is_intro}
                        <!-- Two-Column Layout -->
                        <div class="credit-two-column">                            
                            <div class="title" style={swap_font_sizes_on_two_column ? name_style(false) : title_style(false)} class:uppercase={title_uppercase}>
                                {item.title}
                            </div>
                            <div class="name" style={swap_font_sizes_on_two_column ? title_style(false) : name_style(false)} class:uppercase={name_uppercase}>
                                {item.name}
                            </div>
                        </div>
                    {:else}
                        <!-- Stacked Layout (Default and for Intro) -->
                        <div class="credit" class:intro-block={item.is_intro}>
                            <h2 style={title_style(item.is_intro)} class:uppercase={title_uppercase && !item.is_intro}>{item.title}</h2>
                            {#if item.name}
                                <p style={name_style(item.is_intro)} class:uppercase={name_uppercase && !item.is_intro}>{item.name}</p>
                            {/if}
                        </div>
                    {/if}
                {/if}
            {/each}
        </div>
    {/if}
</div>


<style>
     /* Main container for the scrolling effect */
    .wrapper {
        width: 100%;
        height: 100%;
        overflow: hidden;
        position: relative;
        font-family: sans-serif;
    }
    .scroll-logo-container {                
        text-align: center;
        margin-bottom: 2rem; /* Space between logo and intro text */
    }
    .scroll-logo-container img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 80%;
        object-fit: contain;
    }

    /* Animated container holding all credit items */
    .credits-container {
        position: absolute;
        bottom: 0;
        transform: translateY(100%);
        width: 100%;
        text-align: center;
        animation: scroll var(--animation-duration) linear infinite;
        padding: 0 2rem; /* Adds horizontal padding */
        box-sizing: border-box;
    }

    /* Section Title Style */
    .section-title {
        margin-top: 4rem;
        margin-bottom: 2.5rem;
        font-weight: bold;
    }

    /* Stacked Layout */
    .credit.intro-block {
        margin-bottom: 5rem;
    }
    .credit {
        margin-bottom: 2rem;
    }
    .credit h2, .credit p {
        margin: 0.5rem 0;
        font-family: sans-serif;
    }

    /* Two-Column Layout */
    .credit-two-column {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        text-align: left;
        margin: 0.8rem auto;
        max-width: 80%; /* Limits width for better readability */
        gap: 1rem;
    }
    .credit-two-column .title {
        flex: 1;
        text-align: right;
        padding-right: 1rem;
    }
    .credit-two-column .name {
        flex: 1;
        text-align: left;
        padding-left: 1rem;
    }

    /* Utility class for uppercase */
    .uppercase {
        text-transform: uppercase;
    }

    /* Scroll animation keyframes */
    @keyframes scroll {
        0% { transform: translateY(100%); }
        100% { transform: translateY(-100%); }
    }
</style>