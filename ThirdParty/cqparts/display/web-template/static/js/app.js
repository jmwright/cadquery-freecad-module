// three js local files
//
var container, controls , obj;
var camera, scene, renderer, light;
init();
animate();
function init() {
	container = document.createElement( 'div' );
	document.body.appendChild( container );
	camera = new THREE.PerspectiveCamera( 90, window.innerWidth / window.innerHeight,0.0001);
	camera.position.set(0.5,0.5,0.5);
	controls = new THREE.OrbitControls( camera );
    controls.autoRotate = true;
    controls.autoRotateSpeed = 2;
	controls.target.set(0,0,0);
	controls.update();
    scene = new THREE.Scene({antialias: true});
    scene.background =  new THREE.Color(255,255,255)
    // light 1
	light = new THREE.HemisphereLight( 0xbbbbff, 0x444422 );
	light.position.set( 0, 20, 0 );
    scene.add( light );
    // light 2
	light2 = new THREE.PointLight(0xf0f0f0,2,100);
	light2.position.set( 50,50,50);
	scene.add( light2 );
	// model
	var loader = new THREE.GLTFLoader();
	loader.load( 'model/out.gltf', function ( gltf ) {
		scene.add( gltf.scene );
        obj = gltf.scene;
	} );
	renderer = new THREE.WebGLRenderer( { antialias: true } );
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize( window.innerWidth, window.innerHeight );
	renderer.gammaOutput = true;
	container.appendChild( renderer.domElement );
	window.addEventListener( 'resize', onWindowResize, false );
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

function animate() {
    requestAnimationFrame( animate );
    controls.update();
    renderer.render( scene, camera );
}
