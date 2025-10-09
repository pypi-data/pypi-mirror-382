<!-- StarWarsEffect.svelte -->

<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    /**
     * Props for the StarWarsEffect component.
     * @typedef {Object} Props
     * @property {Array<{title?: string, name?: string, section_title?: string}>} credits - List of credits, can include sections.
     * @property {number} speed - Animation speed in seconds (default: 40).
     * @property {number} base_font_size - Base font size in rem (default: 1.5).
     * @property {string | null} background_color - Background color (default: black).
     * @property {string | null} title_color - Title text color (default: #feda4a).
     * @property {string | null} name_color - Name text color (default: #feda4a).
     * @property {string | null} intro_title - Optional intro title.
     * @property {string | null} intro_subtitle - Optional intro subtitle.
     * @property {"stacked" | "two-column"} layout_style - Layout for credits.
     * @property {boolean} title_uppercase - Transform title to uppercase.
     * @property {boolean} name_uppercase - Transform name to uppercase.
     * @property {boolean} section_title_uppercase - Transform section title to uppercase.
     * @property {boolean} swap_font_sizes_on_two_column - Swap title/name font sizes.
     * @property {{path: string | null, url: string | null, ...} | null} scroll_logo_path - Logo to display inside the scroll.
     * @property {string} scroll_logo_height - Height of the scrolling logo.
     */
    export let credits: Props['credits'];
    export let speed: number = 40;
    export let base_font_size: number = 1.5;
    export let background_color: string | null = null;
    export let title_color: string | null = null;
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
    
    // Reactive styles
    $: title_style = (is_intro: boolean) => `color: ${title_color || '#feda4a'}; font-size: ${is_intro ? base_font_size * 1.5 : base_font_size}rem;`;
    $: name_style = (is_intro: boolean) => `color: ${name_color || '#feda4a'}; font-size: ${is_intro ? base_font_size * 0.9 : base_font_size * 0.7}rem;`;
    $: section_title_style = `color: ${title_color || '#feda4a'}; font-size: ${base_font_size * 1.2}rem;`;

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

    let crawlElement: HTMLElement | null;

    function resetAnimation() {
        if (crawlElement) {
            crawlElement.style.animation = 'none';
            void crawlElement.offsetHeight; // Trigger reflow
            crawlElement.style.animation = '';
        }
    }

    onMount(resetAnimation);
    onDestroy(() => { crawlElement = null; });

    // Trigger reset on prop changes
    $: credits, speed, layout_style, resetAnimation();

    // Generate star shadows for background
    const generate_star_shadows = (count: number, size: string) => {
        let shadows = Array.from({ length: count }, () => `${Math.random() * 2000}px ${Math.random() * 2000}px ${size} white`).join(', ');
        return shadows;
    };
    const small_stars = generate_star_shadows(200, '1px');
    const medium_stars = generate_star_shadows(100, '2px');
    const large_stars = generate_star_shadows(50, '3px');
</script>

<div class="viewport" style:background={background_color || 'black'}>
    <div class="stars small" style="box-shadow: {small_stars};"></div>
    <div class="stars medium" style="box-shadow: {medium_stars};"></div>
    <div class="stars large" style="box-shadow: {large_stars};"></div>

    <div class="crawl" bind:this={crawlElement} style="--animation-duration: {speed}s;">
        {#if scroll_logo_path?.url}
                <div class="scroll-logo-container">
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
                        <span style={swap_font_sizes_on_two_column ? name_style(false) : title_style(false)} class:uppercase={title_uppercase}>{item.title}</span>
                        <span class="spacer"></span>
                        <span style={swap_font_sizes_on_two_column ? title_style(false) : name_style(false)} class:uppercase={name_uppercase}>{item.name}</span>
                    </div>
                {:else}
                    <!-- Stacked Layout -->
                    <div class="credit" class:intro-block={item.is_intro}>
                        <h2 style={title_style(item.is_intro)} class:uppercase={title_uppercase && !item.is_intro}>{item.title}</h2>
                        {#if item.name}<p style={name_style(item.is_intro)} class:uppercase={name_uppercase && !item.is_intro}>{item.name}</p>{/if}
                    </div>
                {/if}
            {/if}
        {/each}
    </div>
</div>

<style>
    
    .viewport {
        width: 100%;
        height: 100%;
        position: relative;
        overflow: hidden;
        perspective: 400px;
        -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
        mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
        font-family: "Droid Sans", sans-serif;
        font-weight: bold;
    }
    .stars {
        position: absolute; top: 0; left: 0;
        width: 1px; height: 1px;
        background: transparent; z-index: 0;
        animation: twinkle 10s linear infinite;
    }
    .stars.small { animation-duration: 10s; }
    .stars.medium { animation-duration: 15s; }
    .stars.large { animation-duration: 20s; }
    @keyframes twinkle { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
    
    .crawl {
        position: absolute; width: 100%; bottom: 0;
        transform-origin: 50% 100%;
        animation: crawl-animation var(--animation-duration) linear infinite;
        z-index: 1; text-align: center;
    }
    @keyframes crawl-animation {
        0% { transform: rotateX(60deg) translateY(100%) translateZ(100px); }
        100% { transform: rotateX(60deg) translateY(-150%) translateZ(-1200px); }
    }
    
    /* STYLES */
    .scroll-logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .scroll-logo-container img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 70%;
        object-fit: contain;    
        filter: grayscale(1) sepia(100%) hue-rotate(15deg) saturate(8) brightness(1.2);
    }
    .uppercase { text-transform: uppercase; }
    
    .section-title {
        margin-top: 5rem;
        margin-bottom: 3rem;
        font-weight: bold;
    }

    .credit.intro-block { margin-bottom: 5rem; }
    .credit { margin-bottom: 2rem; }
    .credit h2, .credit p { margin: 0.5rem 0; padding: 0; white-space: nowrap; }

    .credit-two-column {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin: 0.8rem auto;
        width: 90%;
        white-space: nowrap;
    }
    .credit-two-column .spacer {
        flex-grow: 1;
        border-bottom: 1px dotted rgba(254, 218, 74, 0.3);
        margin: 0 1em;
        transform: translateY(-0.5em);
    }
</style>