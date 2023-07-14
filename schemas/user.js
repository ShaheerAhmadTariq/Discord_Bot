const mongoose=require('mongoose')
const UserSchema=new mongoose.Schema({
user_name:{
    type:String,
    required:true
},
email:{
    type:String,
    required:true
},
last_text_time:{
    type:Number,
    default:0
    
    
},
last_voice_time:{
    type:Number,
    default:0
    
    
},
payment:{
    type:Boolean,
    default:false 
    
}


})

module.exports=mongoose.model('Login',UserSchema)

