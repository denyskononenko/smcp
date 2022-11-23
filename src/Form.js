import React, {Component} from "react";
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import ThreeScene from './Scene.js';
import Summary from "./Summary.js";
import { FlareSharp } from "@mui/icons-material";

const testVertices = [[2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 2, 1], [2, 3, 1], [2, 4, 1]];
const testExchanges = [0.5, 0.1]
const testDistances = [3, 3]
const testEdges = [[[0, 1], [1, 2], [3, 4], [4, 5]], [[0, 3], [1, 4], [2, 5]]];
const testLattice =  [[1, 0, 0], [0, 1, 0], [0, 0, 1]];


class Form extends Component {

    constructor(props){
        super(props);
        this.state = {
            file: null,
            isSpinModelCalculated: false,
            isUploadPending: false, 
            fileName: "no files selected yet",
            lattice: testLattice,
            exchanges: testExchanges,
            distances: testDistances,
            vertices: testVertices,
            edges: testEdges,
            errorMessage: ""
        }
    };

    handleFileChange = (event) => {
        // add file name processing
        this.setState({
            file: event.target.files[0],
            fileName: event.target.files[0].name
        });
        
        console.log("file ", this.state);
    };

    handleFileSubmit = () => {
        // 
        this.setState({isUploadPending: true});

        const data = new FormData();
        // assemble the responce data
        data.append('file', this.state.file);
        
        fetch('/upload', {
        method: 'POST',
        body: data,
        })
        .then(response => response.json())
        .then(data => { this.setState({
            lattice: data.lattice,
            exchanges: data.exchanges,
            distances: data.distances, 
            vertices: data.vertices,
            edges: data.edges, 
            isSpinModelCalculated: data.status, 
            errorMessage: data.error,
            isUploadPending: false
            });
            console.log("Submit is invoked");
            console.log(this.state);
        });
    };

    render(){
        const isSpinModelCalculated = this.state.isSpinModelCalculated;
        const isUploadPending = this.state.isUploadPending;

        let scene;
        let summary;
        let progress;

        if (isUploadPending) {
            progress = <CircularProgress />;
        } else {
            progress = null;
        }

        if (isSpinModelCalculated) {
            scene = <ThreeScene
                        lattice={this.state.lattice}
                        exchanges={this.state.exchanges}
                        distances={this.state.distances}
                        vertices={this.state.vertices} 
                        edges={this.state.edges} />;
            summary = <Summary 
                        exchanges={this.state.exchanges}
                        distances={this.state.distances}
                        />;
        } else {
            scene = <p></p>
            summary = <p>{this.state.errorMessage}</p>;
        }

        return(
            <div className="FormWrapper">
                <h3>Spin Models for Cuprates Predictor</h3>
                <p>This application estimates transfer integrals between Cu2+ sites in undoped cuprates.</p>
                <p>Select .cif file of cuprate structure you are interested in.</p>
                <div className="fileUploadWrapper">
                    <input 
                        type="file" 
                        id="file-upload" 
                        onChange={this.handleFileChange} 
                        style={{display: "none"}} 
                        accept=".cif"/>
                    <label className="uploadButton" htmlFor="file-upload">
                    <Button variant="text" component="span" size="small">Select cif file</Button>
                    </label>
                    <p style={{display: "inline-block"}}>{this.state.fileName}</p>
                    <Button 
                        disabled={this.state.file === null || this.state.isUploadPending} 
                        variant="contained" 
                        size="small" 
                        onClick={this.handleFileSubmit}>Upload</Button>
                    {progress}
                </div>
                {scene}
                {summary}
                {/* <ThreeScene
                    lattice={this.state.lattice}
                    exchanges={this.state.exchanges}
                    distances={this.state.distances}
                    vertices={this.state.vertices} 
                    edges={this.state.edges} />
                <Summary 
                    exchanges={this.state.exchanges}
                    distances={this.state.distances}
                    /> */}
            </div>
        )
    };
}

export default Form;