import React, { Component } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import ExchangeColors from "./declarations.js"

class ThreeScene extends Component {

    componentDidMount(){
        // const backgroundColor = "#C0C0C0";
        const sizes = {width: this.mount.clientWidth, height: this.mount.clientHeight};
        // scene
        this.scene = new THREE.Scene();
        // this.scene.background = new THREE.Color( backgroundColor );
        // init light 
        this.light = new THREE.AmbientLight("#ffffff", 1);
        this.pointLight = new THREE.PointLight("#ffffff", 1, 1000);
        this.pointLight.position.set(20, 20, 20);
        this.pointLight.castShadow = true;
        this.scene.add(this.light);
        this.scene.add(this.pointLight);

        // renderer
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.setSize(sizes.width, sizes.height);
        this.mount.appendChild(this.renderer.domElement);
        // camera
        this.camera = new THREE.PerspectiveCamera(90, sizes.width / sizes.height, 0.05, 100);
        this.camera.position.set(15, 15, 15);
        //controls
        const controls = new OrbitControls(this.camera, this.renderer.domElement);

        // configure controls constrains for maximal zoom in/out in angstroms
        controls.maxDistance = 20;
        controls.minDistance = 6;

        this.addLatticeVectors();
        
        // start rendering
        this.renderScene();
        this.startAnimation();
    };

    componentWillUnmount() {
        //this.stopAnimation();
        this.mount.removeChild(this.renderer.domElement);
    };

    startAnimation = () => {
        if (!this.frameId){
            this.frameId = requestAnimationFrame(this.animate);} 
    };

    stopAnimation = () => {
        cancelAnimationFrame(this.frameId);
    };

    renderScene = () => {
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    };

    animate = () => {
        this.renderScene();
        this.frameId = window.requestAnimationFrame(this.animate);
    };

    makeAtom = (point, radius0, color) => {
        let materialConfig = {
            color: color
        }
        /* Create the atom as a sphere at the given point (x,y,z) */
        let material = new THREE.MeshPhysicalMaterial(materialConfig);
        let radius = radius0;
        let geometry = new THREE.SphereGeometry(radius, 32, 16, 0, Math.PI * 2, 0, Math.PI);
        let sphere = new THREE.Mesh(geometry, material);
        // init coordinates of the atoms
        sphere.position.copy(point.clone());
        return sphere;
    };
    
    makeBond = (point1, point2, radius=0.1, color="#ffffff") => {
        /* Create bond spanned between two points */
        // direction from first to second point
        let direction = new THREE.Vector3().subVectors(point2, point1); 
        // cylinder geometry
        let geometry = new THREE.CylinderGeometry(radius, radius, direction.length(), 8, 4);
        // cylinder material 
        let material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true, 
            opacity: 0.9
        });
        // make the bound mesh
        let position  = point2.clone().add(point1).divideScalar(2);
        let orientation = new THREE.Matrix4(); // new orientation matrix to offset pivot
        let offsetRotation = new THREE.Matrix4(); // matrix to fix pivot rotation
        orientation.lookAt(point1, point2, new THREE.Vector3(0,1,0));//look at destination
        offsetRotation.makeRotationX(Math.PI * 0.5); // rotate 90 degs on X
        orientation.multiply(offsetRotation); // combine orientation with rotation transformations
        geometry.applyMatrix4(orientation)
        // assemble mesh object
        let bond = new THREE.Mesh(geometry, material);
        bond.position.copy(position.clone());
        return bond;
    }; 

    makeArrow = (point1, point2, color="#000000") => {
        /* 
        Create the arrow pointed along the line segment. 
        Arrow consists of the cone (head) and cylinder (body).
        Args:
            point1, point2: (THREE.Vector3) line segment
            color: (str) color of the arrow
        Returns:
            array with cone and cylinder.
        */
        let cylinderRadius = 0.15;
        let coneRadius = 0.3;
        point1.normalize().multiplyScalar(2);
        point2.normalize().multiplyScalar(2);
        /* Add arrow spanned on two points to the scene. */
        // create cylinder
        let cylinder = this.makeBond(point1, point2, cylinderRadius, color);
        // create cone
        let cone = this.makeCone(new THREE.Vector3(point2.x * 1.5, point2.y * 1.5, point2.z * 1.5), point2, coneRadius, color);
        return [cone, cylinder]
    };

    makeCone = (point1, point2, radius=0.3, color="#ffffff") => {
        /* Create the cone spanned between two pooints */
        let direction = new THREE.Vector3().subVectors(point2, point1); 
        // cylinder geometry
        let geometry = new THREE.ConeGeometry(radius, direction.length(), 32);
        // cylinder material 
        let material = new THREE.MeshBasicMaterial({color: color});
        // malign the cone along the line segment 
        let position  = point2.clone().add(point1).divideScalar(2);
        let orientation = new THREE.Matrix4(); // a new orientation matrix to offset pivot
        let offsetRotation = new THREE.Matrix4(); // a matrix to fix pivot rotation
        orientation.lookAt(point1, point2, new THREE.Vector3(0, 1, 0)); //look at destination
        offsetRotation.makeRotationX(Math.PI * 0.5); //rotate 90 degs on X
        orientation.multiply(offsetRotation);//combine orientation with rotation transformations
        geometry.applyMatrix4(orientation)
        // assemble mesh object
        let cone = new THREE.Mesh(geometry, material);
        cone.position.copy(position.clone());
        return cone;
    };

    makeSpinModel = (vertices, exchanges) => {
        /* 
        Create spin model
        Args:
            vertices : array of the Vector3D points, i.e. [ THREE.Vector3(), THREE.Vector3(), ... ]
            exchanges: array of arrays with exchange bonds i.e. [ [ [ i, j ], ... ], ... ] 
        Returns:
            array of atoms and bonds 
        */
        let vertices3DObj = [];
        let edges3DObj = [];
        // create 3D objects for vertices
        vertices.forEach((position) => {
            vertices3DObj.push(this.makeAtom(position, 0.25, "#ffffff"));
        });
        // create 3D objects for exchanges
        exchanges.forEach((edges, exchangeIndex) => {
            edges.forEach((edge) => {
                console.log(vertices[edge[0]], vertices[edge[1]], ExchangeColors[exchangeIndex]);
                edges3DObj.push(this.makeBond(vertices[edge[0]], vertices[edge[1]], 0.1, ExchangeColors[exchangeIndex]));
            });
        });
        return vertices3DObj.concat(edges3DObj);
    };

    makeLatticeVectors = (a, b, c) => {
        /* Make 3D obects of lattice vectors */
        let o = new THREE.Vector3(0, 0, 0);
        return this.makeArrow(o, a, "#f54242").concat(this.makeArrow(o, b, "#00ff3c"), this.makeArrow(o, c, "#006eff"));
    };

    addLatticeVectors = () => {
        /* Add lattice vectors 3D objects to the scene */
        // convert lattice vectors from [x,y,z] to THREE.Vector3
        let lattice = [];
        this.props.lattice.forEach((latvec) => {
            lattice.push(new THREE.Vector3(...latvec));
        });
        // lattice vectors arrows
        this.scene.add(...this.makeLatticeVectors(...lattice));
    };

    addSpinModel = () => {
        /* Add the spin model to the scene */
        let vertices = [];
        // convert vertices from array [x,y,z] to THREE.Vector3
        this.props.vertices.forEach((vertice) => {
            vertices.push(new THREE.Vector3(...vertice));
        });
        // spin model to the scene 
        this.scene.add(...this.makeSpinModel(vertices, this.props.edges));
        
    };

    componentDidUpdate = (prevProps) => { 
        console.log("Component did update");
        console.log("Prev props: ", prevProps);
        console.log("New props: ", this.props);
        // clear scene
        while(this.scene.children.length > 0){ 
            this.scene.remove(this.scene.children[0]); 
        }
        // add arrows to the scene
        this.scene.add(this.light);
        this.scene.add(this.pointLight);
        this.addLatticeVectors();
        this.addSpinModel();
    };

    render(){
        return(
            <div 
                className="sceneWrapper" 
                ref={ mount => { this.mount = mount } } 
            />
        )
    }
}

export default ThreeScene;