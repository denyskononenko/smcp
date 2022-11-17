import React, {Component} from "react";
import Button from '@mui/material/Button';
import ThreeScene from './Scene.js';
import Summary from "./Summary.js";

const testVertices = [[2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 2, 1], [2, 3, 1], [2, 4, 1]];
const testExchanges = [0.5, 0.1]
const testEdges = [[[0, 1], [1, 2], [3, 4], [4, 5]], [[0, 3], [1, 4], [2, 5]]];
const testLattice =  [[1, 0, 0], [0, 1, 0], [0, 0, 1]];

class Form extends Component {

    constructor(props){
        super(props);
        this.state = {
            file: null,
            fileName: "no files selected yet",
            vertices: testVertices,
            edges: testEdges,
            exchanges: testExchanges,
            lattice: testLattice
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
        const data = new FormData();
        // assemble the responce data
        data.append('file', this.state.file);
        
        fetch('/upload', {
        method: 'POST',
        body: data,
        })
        .then(response => response.json())
        .then(data => { this.setState({
            exchanges: data.exchanges, 
            vertices: data.vertices,
            edges: data.edges, 
            lattice: data.lattice });
            console.log("Submit is invoked");
            console.log(this.state);
        });
    };

    render(){
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
                    <Button disabled={this.state.file === null} variant="contained" size="small" onClick={this.handleFileSubmit}>Upload</Button>
                </div>
                <ThreeScene vertices={this.state.vertices} edges={this.state.edges} lattice={this.state.lattice}/>
                <Summary exchanges={this.state.exchanges}/>
            </div>
        )
    };
}

export default Form;