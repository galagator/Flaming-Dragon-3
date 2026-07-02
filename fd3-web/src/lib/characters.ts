// Single source of truth for the FD3 cast.
// Was previously duplicated in index.html, character-studio.html, and
// partially in face-tagger.html. Server is authoritative for stats; this
// file is the static metadata (name, role, costume, scenes, dialogue).

export type Status = 'shot' | 'missing' | 'ai';
// Tuple form keeps the data compact: scenes: [['Scene 1', 'shot'], ...]
export type Scene = [name: string, status: Status];
export interface Character {
	name: string;
	role: string;
	status: Status;
	costume: string;
	scenes: Scene[];
	dialogue: string[];
}

export const CHARACTERS: Character[] = [
	{
		name: 'Galen / Ji-lan',
		role: 'Antagonist, GKD Cult Leader',
		status: 'shot',
		costume: "Black polo with 'VO' logo, receding brown hair, full beard, blue eyes. Cult-leader infomercial vibe.",
		scenes: [['GKD Commercial','shot'],['Scene 8B','missing'],['Scene 8C','missing'],['Scene 8D','missing'],['Scene 9','missing'],['Scene 13','missing']],
		dialogue: [
			'When I was young I came to this country with nothing but the headband on my head and a fire in my heart.',
			"Let's try this one more time. I'll bring the contract over and you sign it.",
			"Well I guess we'll do this the hard way.",
			'SIGN THE CONTRACT.',
			'You two, go take care of him.',
			'Slarth, Trubble, show them what the GKD Elite can do!',
			"Tony, as you may or may not know we have your precious MAMA.",
			'Just be there doughboy.',
			"Why did it have to come to this? All I wanted was for a Chinatown that was free of any other cultures interfering.",
		]
	},
	{
		name: 'Tony',
		role: 'Protagonist, The Flaming Dragon',
		status: 'shot',
		costume: 'Asian male, glasses, dark hair in ponytail/bun. White button-down shirt, business-casual. Later: Flaming Dragon headband + costume.',
		scenes: [['Scene 1','shot'],['Scene 2','shot'],['Scene 3','shot'],['Scene 4','shot'],['Scene 5','shot'],['Scene 6','shot'],['Scene 7','missing'],['Scene 8A','missing'],['Scene 8C','missing'],['Scene 9','missing'],['Scene 10','missing'],['Scene 11','missing'],['Scene 12','missing'],['Scene 13','missing']],
		dialogue: [
			'Wow GKD looks so powerful.',
			'Hey guys why do you even bother with fighting — we should all make love not war!',
			"I'll defend myself with my sexy saxophone riffs so everyone will just calm down.",
			'Is mamma home yet??',
			'You need to train me, I think the GKD have got mama.',
			"I don't get it.",
			"Can't we just get to breaking boards like karate on the movies?",
			"Where's my MAMA??",
			"It's Fettuccini!!!!!!!",
			'I AM THE FLAMING DRAGON!',
		]
	},
	{
		name: 'Yake-oh',
		role: "Tony's friend, Kung Fu trainer",
		status: 'shot',
		costume: 'Caucasian, blonde man bun, large black ear tunnels (gauges), denim jacket, goatee, laid-back stoner vibe.',
		scenes: [['Scene 1','shot'],['Scene 6','shot'],['Scene 8A','missing'],['Scene 8C','missing'],['Scene 8E','missing'],['Scene 9','missing'],['Scene 11','missing'],['Scene 13','missing']],
		dialogue: [
			"Man that's some corny shit.",
			"Come on man, we're just having fun… You might need to know how to defend yourself one day.",
			"What happened to your face mate, did you go diving in pasta sauce??",
			"OK relax, don't do it… When you wanna go do it? When you wanna train?",
			"Alright Tony, it's just you and me tomorrow at first light…",
			"Alright mate, the first thing you need to know is flow like water and be light like air.",
			"You're still not getting it. FLOW LIKE WATER!",
			"Let's get out of here!",
			"OH DAMN IT'S THE FLAMING DRAGON, Tony IS THAT YOU??",
		]
	},
	{
		name: 'Erb Dean',
		role: "Tony's stoner friend",
		status: 'shot',
		costume: 'Caucasian, dreadlocks under beanie, camo shirt, barefoot, Rastafarian/hippie style.',
		scenes: [['Scene 1','shot'],['Scene 6','shot'],['Scene 9','missing'],['Scene 11','missing'],['Scene 13','missing']],
		dialogue: [
			"He's just a sell out mon, I bet he can't even downward dog.",
			"I'd like to see this guy try a FLAMING DRAGON death blow.",
			"Ya mums not cut out!",
			"Notice how the lights are still off in the kitchen, no way she be home yet.",
			"You meant to put the erbs in the pasta sauce not smoke it.",
			"Count me out, there's a big Kung Fu party at the old dirt bowl tomorrow.",
			"Wag'wan mi bredren! Me feel as if you seen dem duppys…",
			'FLAME ON FOREVER BRUDDDA!',
		]
	},
	{
		name: 'MAMA',
		role: 'Italian restaurant owner, mother figure',
		status: 'shot',
		costume: 'Asian woman (older), red apron with snowflake pattern, white shirt, frazzled waitress look.',
		scenes: [['Scene 3','shot'],['Scene 8B','missing'],['Scene 13','missing']],
		dialogue: [
			"Tony, I'm glad you're here. Since your father died it's been so hard to knead the dough with my frail old hands.",
			"Hey you two get outta here, I told you we won't sign nothing!",
			"I don't know what I'd do without the restaurant, we've been here for years!",
			"I ain't signing no contract, not even for all the gnocchi in sicily.",
			'Get away from me you vile beast of a man.',
			"Don't you touch my baby boy!",
			'What you mean… You people???',
		]
	},
	{
		name: 'Trubble',
		role: 'GKD goon',
		status: 'shot',
		costume: 'Short brown hair, light stubble, full sleeve tattoo (left arm), black t-shirt with white text, brown work boots.',
		scenes: [['Scene 2','shot'],['Scene 3','shot'],['Scene 4','shot'],['Scene 8B','missing'],['Scene 8D','missing'],['Scene 8E','missing'],['Scene 13','missing']],
		dialogue: [
			'Oh yes you will.',
			"Ha, this guy definitely ain't stopping us.",
			"Our boss is a patient man but his patience is running thin 'mama'.",
			"Stay out of our way you spineless doughboy.",
			"You shouldn't have followed us doughboy, GKD has no time for pasta pushers like you.",
			"Let's go pay mama another visit.",
			'Boss, you might want to see this.',
		]
	},
	{
		name: 'Slarth',
		role: 'GKD goon',
		status: 'shot',
		costume: 'Dark hoodie/jacket, dark clothing. Partially visible — plays second goon to Trubble.',
		scenes: [['Scene 2','shot'],['Scene 3','shot'],['Scene 4','shot'],['Scene 8B','missing'],['Scene 8D','missing'],['Scene 8E','missing'],['Scene 13','missing']],
		dialogue: [
			'We always get what we want.',
			'What a flamin joke…',
			"Yeah, you better watch your step 'mama'.",
			'Get him!',
			"Hey its Doughboy and his boyfriend training in the park.",
			"Yeah let's show these ravioli rollers what happens when you mess with the GKD.",
		]
	},
	{
		name: 'Zoh-baggo',
		role: 'Female GKD goon',
		status: 'ai',
		costume: 'Female business-casual (office goon attire). Breaks a heel during the park fight. Needs AI generation.',
		scenes: [['Scene 8B','missing'],['Scene 8C','missing'],['Scene 8E','missing'],['Scene 13','missing']],
		dialogue: ['Heyyy dough boy.']
	},
	{
		name: 'TK-Maxx',
		role: 'GKD goon',
		status: 'ai',
		costume: 'Goon attire. Fights Erb Dean, gets KO\'d by Yake-oh. Needs AI generation.',
		scenes: [['Scene 8B','missing'],['Scene 8C','missing'],['Scene 8E','missing'],['Scene 13','missing']],
		dialogue: [
			'How dare you train in GKD territory, now we\'re gonna make you pay!',
			"Don't worry your little fettuncino brain about that, show me what you got!",
		]
	},
	{
		name: 'Jasmine',
		role: "Tony's love interest",
		status: 'ai',
		costume: "Party attire (seen at Dirt Bowl). 'White belt in Suq yo Wang.' Needs AI generation.",
		scenes: [['Scene 11','missing'],['Scene 12','missing'],['Scene 13','missing']],
		dialogue: [
			'Give me your flaming dragon spaghetti and meatballs.',
			'Are you sure you want to do this? Can you match up to the power of GKD?',
			"Well if you're going, I'm going too — I have a white belt in Suq yo Wang.",
		]
	}
];

// Characters list (slim) for the tagger — includes "Not in film" as a sink.
export const TAGGER_CHARS = [...CHARACTERS.map(c => c.name), 'Not in film'];

// Char display name -> filename prefix used in character-references/.
export const REF_PREFIX: Record<string, string> = {
	'Galen / Ji-lan': 'Galen-Ji-lan',
	'Tony': 'Tony',
	'Yake-oh': 'Yake-oh',
	'Erb Dean': 'Erb_Dean',
	'MAMA': 'MAMA',
	'Trubble': 'Trubble',
	'Slarth': 'Slarth',
	'Zoh-baggo': 'Zoh-baggo',
	'TK-Maxx': 'TK-Maxx',
	'Jasmine': 'Jasmine'
};

export function refPrefix(name: string): string {
	return REF_PREFIX[name] ?? name;
}

export function fallbackRefUrl(name: string, n: number): string {
	return `character-references/${refPrefix(name)}${String(n).padStart(2,'0')}.jpg`;
}

// Fallback when /api/references hasn't loaded: synthesize numeric URLs.
export function fallbackRefUrls(name: string, count = 24): string[] {
	return Array.from({ length: count }, (_, i) => fallbackRefUrl(name, i + 1));
}
